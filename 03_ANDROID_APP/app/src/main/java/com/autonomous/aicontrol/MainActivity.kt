package com.autonomous.aicontrol

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Matrix
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.autonomous.aicontrol.ai.YoloDetector
import com.autonomous.aicontrol.decision.DecisionEngine
import com.autonomous.aicontrol.network.UdpVehicleClient
import com.autonomous.aicontrol.ui.OverlayView
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {

    private lateinit var previewView: PreviewView
    private lateinit var overlayView: OverlayView
    private lateinit var tvFps: TextView
    private lateinit var tvInference: TextView
    private lateinit var tvCarStatus: TextView
    private lateinit var tvCurrentAction: TextView
    private lateinit var tvSignInfo: TextView
    private lateinit var btnToggleMode: Button
    private lateinit var btnEmergencyStop: Button

    private lateinit var cameraExecutor: ExecutorService
    private var detector: YoloDetector? = null
    private val decisionEngine = DecisionEngine()
    private val udpClient = UdpVehicleClient("192.168.4.1", 8888)

    private var isManualMode = false
    private var lastFrameTime = System.currentTimeMillis()

    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.INTERNET,
            Manifest.permission.ACCESS_WIFI_STATE
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        previewView = findViewById(R.id.previewView)
        overlayView = findViewById(R.id.overlayView)
        tvFps = findViewById(R.id.tvFps)
        tvInference = findViewById(R.id.tvInference)
        tvCarStatus = findViewById(R.id.tvCarStatus)
        tvCurrentAction = findViewById(R.id.tvCurrentAction)
        tvSignInfo = findViewById(R.id.tvSignInfo)
        btnToggleMode = findViewById(R.id.btnToggleMode)
        btnEmergencyStop = findViewById(R.id.btnEmergencyStop)

        cameraExecutor = Executors.newSingleThreadExecutor()

        // Init Neural Network Detector
        try {
            detector = YoloDetector(this, "yolov8n.tflite", confThreshold = 0.60f)
            Toast.makeText(this, "YOLOv8n Neural Engine Ready", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Warning: Model file missing from assets", Toast.LENGTH_LONG).show()
        }

        // Setup Controls
        btnToggleMode.setOnClickListener {
            isManualMode = !isManualMode
            btnToggleMode.text = if (isManualMode) "MANUAL MODE" else "AUTO MODE"
            if (isManualMode) {
                udpClient.sendCommand("STOP", 0)
            }
        }

        btnEmergencyStop.setOnClickListener {
            isManualMode = true
            btnToggleMode.text = "MANUAL MODE"
            decisionEngine.emergencyStop()
            udpClient.emergencyStop()
            tvCurrentAction.text = "ACTION: EMERGENCY STOP (LOCKED)"
            Toast.makeText(this, "EMERGENCY BRAKE ENGAGED", Toast.LENGTH_SHORT).show()
        }

        if (allPermissionsGranted()) {
            startCamera()
        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS)
        }
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

            // High-Performance Frame Analyzer
            val imageAnalyzer = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                .build()
                .also {
                    it.setAnalyzer(cameraExecutor) { imageProxy ->
                        processCameraFrame(imageProxy)
                    }
                }

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageAnalyzer)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun processCameraFrame(imageProxy: ImageProxy) {
        val t0 = System.currentTimeMillis()
        val bitmap = imageProxyToBitmap(imageProxy)
        imageProxy.close()

        if (bitmap == null) return

        // 1. Run On-Device AI Inference
        val detections = detector?.detect(bitmap) ?: emptyList()
        val dtInference = System.currentTimeMillis() - t0

        // 2. Update Autonomous Decision Engine
        val decision = decisionEngine.processDetections(detections, isManualMode)

        // 3. Dispatch Wireless UDP Command to ESP8266
        if (!isManualMode) {
            udpClient.sendCommand(decision.command, decision.speed)
        }

        // 4. Update Cockpit HUD on UI Thread
        val now = System.currentTimeMillis()
        val fps = 1000f / maxOf(1f, (now - lastFrameTime).toFloat())
        lastFrameTime = now

        runOnUiThread {
            overlayView.setResults(detections, decision)
            tvFps.text = "FPS: ${"%.1f".format(fps)}"
            tvInference.text = "AI: ${dtInference}ms"

            val pingText = if (udpClient.isConnected) "${udpClient.lastPingMs}ms" else "DISCONNECTED"
            tvCarStatus.text = "CAR UDP: $pingText"

            tvCurrentAction.text = "ACTION: ${decision.statusMessage}"
            tvSignInfo.text = "TARGET: ${decision.targetSignName.uppercase()} | ZONE: ${decision.distanceZone}"
        }
    }

    @androidx.annotation.OptIn(androidx.camera.core.ExperimentalGetImage::class)
    private fun imageProxyToBitmap(imageProxy: ImageProxy): Bitmap? {
        val image = imageProxy.image ?: return null
        val planes = image.planes
        val buffer = planes[0].buffer
        val pixelStride = planes[0].pixelStride
        val rowStride = planes[0].rowStride
        val rowPadding = rowStride - pixelStride * image.width

        val bitmap = Bitmap.createBitmap(
            image.width + rowPadding / pixelStride,
            image.height,
            Bitmap.Config.ARGB_8888
        )
        bitmap.copyPixelsFromBuffer(buffer)

        // Rotate if sensor is oriented vertically
        val rotationDegrees = imageProxy.imageInfo.rotationDegrees
        if (rotationDegrees != 0) {
            val matrix = Matrix()
            matrix.postRotate(rotationDegrees.toFloat())
            return Bitmap.createBitmap(bitmap, 0, 0, image.width, image.height, matrix, true)
        }
        return bitmap
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                startCamera()
            } else {
                Toast.makeText(this, "Camera & WiFi permissions are required.", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        udpClient.close()
        detector?.close()
        cameraExecutor.shutdown()
    }
}
