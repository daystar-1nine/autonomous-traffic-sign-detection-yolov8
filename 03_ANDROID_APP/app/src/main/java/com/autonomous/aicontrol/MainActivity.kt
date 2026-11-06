package com.autonomous.aicontrol

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Matrix
import android.os.Bundle
import android.view.KeyEvent
import android.view.MotionEvent
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
import com.autonomous.aicontrol.controller.*
import com.autonomous.aicontrol.decision.DecisionEngine
import com.autonomous.aicontrol.network.UdpVehicleClient
import com.autonomous.aicontrol.ui.OverlayView
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity(), ControllerEventListener, ControlModeListener {

    // Views
    private lateinit var previewView: PreviewView
    private lateinit var overlayView: OverlayView
    private lateinit var tvModeIndicator: TextView
    private lateinit var tvGamepadStatus: TextView
    private lateinit var tvFps: TextView
    private lateinit var tvInference: TextView
    private lateinit var tvCarStatus: TextView

    private lateinit var tvDiagDeviceName: TextView
    private lateinit var tvDiagLeftStick: TextView
    private lateinit var tvDiagRightStick: TextView
    private lateinit var tvDiagTriggers: TextView
    private lateinit var tvDiagButtons: TextView
    private lateinit var tvMotorOutputs: TextView

    private lateinit var tvCurrentAction: TextView
    private lateinit var tvSignInfo: TextView
    private lateinit var tvSpeedProfile: TextView

    private lateinit var btnManualMode: Button
    private lateinit var btnAutoMode: Button
    private lateinit var btnEmergencyStop: Button

    // System Components
    private lateinit var cameraExecutor: ExecutorService
    private var detector: YoloDetector? = null
    private val decisionEngine = DecisionEngine()
    private val udpClient = UdpVehicleClient("192.168.4.1", 8888)

    // Controller & Drive Managers
    private lateinit var aresController: AresProController
    private val differentialDrive = DifferentialDriveController(SpeedProfile.NORMAL)
    private lateinit var modeManager: ControlModeManager

    private var lastFrameTime = System.currentTimeMillis()
    private var isCameraPipelineReady = false

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

        // Bind Views
        previewView = findViewById(R.id.previewView)
        overlayView = findViewById(R.id.overlayView)
        tvModeIndicator = findViewById(R.id.tvModeIndicator)
        tvGamepadStatus = findViewById(R.id.tvGamepadStatus)
        tvFps = findViewById(R.id.tvFps)
        tvInference = findViewById(R.id.tvInference)
        tvCarStatus = findViewById(R.id.tvCarStatus)

        tvDiagDeviceName = findViewById(R.id.tvDiagDeviceName)
        tvDiagLeftStick = findViewById(R.id.tvDiagLeftStick)
        tvDiagRightStick = findViewById(R.id.tvDiagRightStick)
        tvDiagTriggers = findViewById(R.id.tvDiagTriggers)
        tvDiagButtons = findViewById(R.id.tvDiagButtons)
        tvMotorOutputs = findViewById(R.id.tvMotorOutputs)

        tvCurrentAction = findViewById(R.id.tvCurrentAction)
        tvSignInfo = findViewById(R.id.tvSignInfo)
        tvSpeedProfile = findViewById(R.id.tvSpeedProfile)

        btnManualMode = findViewById(R.id.btnManualMode)
        btnAutoMode = findViewById(R.id.btnAutoMode)
        btnEmergencyStop = findViewById(R.id.btnEmergencyStop)

        cameraExecutor = Executors.newSingleThreadExecutor()

        // Initialize Managers
        modeManager = ControlModeManager(this)
        aresController = AresProController(this, this)

        // Init Neural Network Detector
        try {
            detector = YoloDetector(this, "yolov8n.tflite", confThreshold = 0.60f)
            Toast.makeText(this, "YOLOv8n Neural Engine Ready", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Model ready in assets", Toast.LENGTH_SHORT).show()
        }

        setupButtons()
        updateModeUi(modeManager.currentMode)
        updateProfileUi(differentialDrive.currentProfile)

        if (allPermissionsGranted()) {
            startCamera()
        } else {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS)
        }
    }

    private fun setupButtons() {
        btnManualMode.setOnClickListener {
            if (modeManager.isEmergencyStop()) {
                modeManager.resetEmergencyStop(ControlMode.MANUAL)
            } else {
                modeManager.setManualMode(aresController.isConnected(), "Manual Button Tapped")
            }
        }

        btnAutoMode.setOnClickListener {
            if (modeManager.isEmergencyStop()) {
                modeManager.resetEmergencyStop(ControlMode.AUTONOMOUS)
            } else {
                modeManager.setAutonomousMode(isCameraPipelineReady, "Auto Button Tapped")
            }
        }

        btnEmergencyStop.setOnClickListener {
            modeManager.triggerEmergencyStop("UI Stop Button")
        }

        tvSpeedProfile.setOnClickListener {
            val newProfile = differentialDrive.cycleSpeedProfile()
            updateProfileUi(newProfile)
        }
    }

    private fun updateModeUi(mode: ControlMode) {
        runOnUiThread {
            when (mode) {
                ControlMode.MANUAL -> {
                    tvModeIndicator.text = "[MODE: MANUAL]"
                    tvModeIndicator.setTextColor(ContextCompat.getColor(this, R.color.hud_orange))
                    tvCurrentAction.text = "ACTION: MANUAL CONTROLLER ACTIVE"
                    tvCurrentAction.setTextColor(ContextCompat.getColor(this, R.color.hud_orange))
                    btnManualMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_orange))
                    btnAutoMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_gray))
                }
                ControlMode.AUTONOMOUS -> {
                    tvModeIndicator.text = "[MODE: AUTONOMOUS AI]"
                    tvModeIndicator.setTextColor(ContextCompat.getColor(this, R.color.hud_cyan))
                    tvCurrentAction.text = "ACTION: AI VISION TRACKING"
                    tvCurrentAction.setTextColor(ContextCompat.getColor(this, R.color.hud_cyan))
                    btnAutoMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_cyan))
                    btnManualMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_gray))
                }
                ControlMode.EMERGENCY_STOP -> {
                    tvModeIndicator.text = "[EMERGENCY STOP (LOCKED)]"
                    tvModeIndicator.setTextColor(ContextCompat.getColor(this, R.color.hud_red))
                    tvCurrentAction.text = "ACTION: EMERGENCY BRAKE ENGAGED"
                    tvCurrentAction.setTextColor(ContextCompat.getColor(this, R.color.hud_red))
                    btnManualMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_gray))
                    btnAutoMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_gray))
                }
            }
        }
    }

    private fun updateProfileUi(profile: SpeedProfile) {
        runOnUiThread {
            tvSpeedProfile.text = "PROFILE: ${profile.displayName} [Press Y / Tap to Cycle]"
        }
    }

    // ----------------- CONTROLLER EVENT DISPATCHING -----------------

    override fun dispatchGenericMotionEvent(event: MotionEvent): Boolean {
        if (aresController.handleMotionEvent(event)) {
            return true
        }
        return super.dispatchGenericMotionEvent(event)
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (event.action == KeyEvent.ACTION_DOWN) {
            if (aresController.handleKeyDown(event.keyCode, event)) {
                return true
            }
        } else if (event.action == KeyEvent.ACTION_UP) {
            if (aresController.handleKeyUp(event.keyCode, event)) {
                return true
            }
        }
        return super.dispatchKeyEvent(event)
    }

    // ----------------- CONTROLLER EVENT LISTENER -----------------

    override fun onJoystickMoved(axisX: Float, axisY: Float) {
        if (modeManager.isManual()) {
            val outputs = differentialDrive.computeMotorOutputs(axisX, axisY)
            udpClient.sendDriveCommand(outputs.leftPwm, outputs.rightPwm)

            runOnUiThread {
                tvMotorOutputs.text = "MOTORS: L: ${outputs.leftPwm} | R: ${outputs.rightPwm} PWM"
                tvCurrentAction.text = "MANUAL: Throttle ${"%.2f".format(-axisY)} | Steer ${"%.2f".format(axisX)}"
            }
        }
    }

    override fun onButtonActionTriggered(action: ControllerButtonAction) {
        when (action) {
            ControllerButtonAction.ENABLE_MANUAL -> {
                if (modeManager.isEmergencyStop()) {
                    modeManager.resetEmergencyStop(ControlMode.MANUAL)
                } else {
                    modeManager.setManualMode(aresController.isConnected(), "Gamepad Button A")
                }
            }
            ControllerButtonAction.ENABLE_AUTONOMOUS -> {
                if (modeManager.isEmergencyStop()) {
                    modeManager.resetEmergencyStop(ControlMode.AUTONOMOUS)
                } else {
                    modeManager.setAutonomousMode(isCameraPipelineReady, "Gamepad Button B")
                }
            }
            ControllerButtonAction.EMERGENCY_STOP -> {
                modeManager.triggerEmergencyStop("Gamepad Button X Pressed")
            }
            ControllerButtonAction.CYCLE_SPEED_PROFILE -> {
                val newProfile = differentialDrive.cycleSpeedProfile()
                updateProfileUi(newProfile)
                Toast.makeText(this, "Profile: ${newProfile.displayName}", Toast.LENGTH_SHORT).show()
            }
            ControllerButtonAction.DECREASE_SPEED -> {
                val newProfile = differentialDrive.setSpeedProfileByIndex(
                    (differentialDrive.currentProfile.ordinal - 1).coerceAtLeast(0)
                )
                updateProfileUi(newProfile)
            }
            ControllerButtonAction.INCREASE_SPEED -> {
                val newProfile = differentialDrive.setSpeedProfileByIndex(
                    (differentialDrive.currentProfile.ordinal + 1).coerceAtMost(SpeedProfile.values().size - 1)
                )
                updateProfileUi(newProfile)
            }
        }
    }

    override fun onControllerConnectionChanged(connected: Boolean, deviceName: String) {
        runOnUiThread {
            if (connected) {
                tvGamepadStatus.text = "[GAMEPAD: $deviceName]"
                tvGamepadStatus.setTextColor(ContextCompat.getColor(this, R.color.hud_green))
                tvDiagDeviceName.text = "Device: $deviceName (Connected)"
                Toast.makeText(this, "Ares Pro Connected: $deviceName", Toast.LENGTH_SHORT).show()
            } else {
                tvGamepadStatus.text = "[GAMEPAD: DISCONNECTED]"
                tvGamepadStatus.setTextColor(ContextCompat.getColor(this, R.color.hud_red))
                tvDiagDeviceName.text = "Device: Disconnected"
                Toast.makeText(this, "Gamepad Disconnected", Toast.LENGTH_SHORT).show()
                modeManager.handleControllerDisconnected()
            }
        }
    }

    override fun onDiagnosticsUpdated(diagnosticData: GamepadDiagnosticData) {
        runOnUiThread {
            tvDiagLeftStick.text = "L-Stick: X: ${"%.2f".format(diagnosticData.leftStickX)} | Y: ${"%.2f".format(diagnosticData.leftStickY)}"
            tvDiagRightStick.text = "R-Stick: X: ${"%.2f".format(diagnosticData.rightStickX)} | Y: ${"%.2f".format(diagnosticData.rightStickY)}"
            tvDiagTriggers.text = "Triggers: LT: ${"%.2f".format(diagnosticData.leftTrigger)} | RT: ${"%.2f".format(diagnosticData.rightTrigger)}"

            val btnStr = if (diagnosticData.activeButtons.isNotEmpty()) {
                diagnosticData.activeButtons.joinToString(", ")
            } else {
                "None"
            }
            tvDiagButtons.text = "Buttons: $btnStr"
        }
    }

    // ----------------- CONTROL MODE LISTENER -----------------

    override fun onModeChanged(oldMode: ControlMode, newMode: ControlMode, reason: String) {
        // Immediate Transition Invariant: Halt motors on any mode switch
        differentialDrive.reset()
        udpClient.sendDriveCommand(0, 0)

        updateModeUi(newMode)
        runOnUiThread {
            Toast.makeText(this, "Mode: $newMode ($reason)", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onEmergencyStopTriggered(source: String) {
        differentialDrive.reset()
        decisionEngine.emergencyStop()
        udpClient.emergencyStop()
        updateModeUi(ControlMode.EMERGENCY_STOP)
        runOnUiThread {
            tvMotorOutputs.text = "MOTORS: L: 0 | R: 0 PWM"
            Toast.makeText(this, "EMERGENCY STOP ENGAGED ($source)", Toast.LENGTH_LONG).show()
        }
    }

    override fun onEmergencyStopReset() {
        runOnUiThread {
            Toast.makeText(this, "Emergency Stop Cleared. Driving Enabled.", Toast.LENGTH_SHORT).show()
        }
    }

    // ----------------- CAMERAX & AI INFERENCE -----------------

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

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
                isCameraPipelineReady = true
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

        // 2. Evaluate Autonomous Decision Engine
        val isAutonomous = modeManager.isAutonomous()
        val decision = decisionEngine.processDetections(detections, manualOverride = !isAutonomous)

        // 3. Dispatch Wireless UDP Command ONLY when in Autonomous Mode
        if (isAutonomous) {
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

            if (isAutonomous) {
                tvCurrentAction.text = "AUTO: ${decision.statusMessage}"
                tvSignInfo.text = "TARGET: ${decision.targetSignName.uppercase()} | ZONE: ${decision.distanceZone}"
            } else if (modeManager.isManual()) {
                tvSignInfo.text = "AI DETECTED: ${if (detections.isNotEmpty()) detections[0].className.uppercase() else "NONE"}"
            }
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
        aresController.release()
        udpClient.close()
        detector?.close()
        cameraExecutor.shutdown()
    }
}
