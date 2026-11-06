package com.autonomous.aicontrol

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.Matrix
import android.os.Bundle
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.Surface
import android.view.View
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
    private lateinit var btnAutoToggleRun: Button
    private lateinit var btnEmergencyStop: Button

    // Autonomous Mode State: false = Standby (Vision active, motors 0), true = Active Driving
    private var isAutonomousRunning: Boolean = false

    // System Components
    private lateinit var cameraExecutor: ExecutorService
    private var detector: YoloDetector? = null
    private val decisionEngine = DecisionEngine()
    private val udpClient = UdpVehicleClient("192.168.4.1", 8888)

    // Controller & Drive Managers
    private lateinit var aresController: AresProController
    private val differentialDrive = DifferentialDriveController(SpeedProfile.SPORT)
    private lateinit var modeManager: ControlModeManager

    // Active Safety (ADAS AEB) & Controller Input Cache
    @Volatile private var isForwardObstacleHazard: Boolean = false
    @Volatile private var hazardName: String = "CLEAR"
    private var vibrator: android.os.Vibrator? = null
    private var manualRotationOffset: Int = 0

    private var lastAxisX: Float = 0f
    private var lastAxisY: Float = 0f
    private var lastRt: Float = 0f
    private var lastLt: Float = 0f
    private var lastTurbo: Boolean = false

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
        btnAutoToggleRun = findViewById(R.id.btnAutoToggleRun)
        btnEmergencyStop = findViewById(R.id.btnEmergencyStop)

        cameraExecutor = Executors.newSingleThreadExecutor()

        // Initialize Managers
        modeManager = ControlModeManager(this)
        aresController = AresProController(this, this)
        vibrator = getSystemService(Context.VIBRATOR_SERVICE) as? android.os.Vibrator

        // Init Neural Network Detector (ONNX Runtime Engine)
        try {
            detector = YoloDetector(this, "yolov8n.onnx", confThreshold = 0.28f)
            if (detector?.isReady() == true) {
                Toast.makeText(this, "YOLOv8n ONNX Neural Engine Active", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Warning: ONNX Session Failed", Toast.LENGTH_LONG).show()
            }
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Model Error: ${e.message}", Toast.LENGTH_LONG).show()
        }

        // Reset camera rotation offset to 0 by default to prevent stuck 90-degree sideways orientation
        manualRotationOffset = 0
        getSharedPreferences("ai_car_prefs", MODE_PRIVATE).edit().putInt("cam_rotation_offset", 0).apply()

        tvInference.setOnClickListener {
            manualRotationOffset = (manualRotationOffset + 90) % 360
            getSharedPreferences("ai_car_prefs", MODE_PRIVATE).edit().putInt("cam_rotation_offset", manualRotationOffset).apply()
            val orientLabel = when (manualRotationOffset) {
                0 -> "0° [Normal Landscape]"
                90 -> "90° [Portrait]"
                180 -> "180° [Reverse Landscape]"
                270 -> "270° [Inverted]"
                else -> "${manualRotationOffset}°"
            }
            Toast.makeText(this, "Camera Orientation: $orientLabel", Toast.LENGTH_SHORT).show()
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

        btnAutoToggleRun.setOnClickListener {
            toggleAutoRunStandby()
        }

        btnEmergencyStop.setOnClickListener {
            modeManager.triggerEmergencyStop("UI Stop Button")
        }

        tvSpeedProfile.setOnClickListener {
            val newProfile = differentialDrive.cycleSpeedProfile()
            updateProfileUi(newProfile)
        }
    }

    private fun toggleAutoRunStandby() {
        if (!modeManager.isAutonomous()) return

        isAutonomousRunning = !isAutonomousRunning
        triggerHapticAlert()

        runOnUiThread {
            if (isAutonomousRunning) {
                btnAutoToggleRun.text = "⏸ STANDBY"
                btnAutoToggleRun.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_orange))
                Toast.makeText(this, "Mission STARTED (Autonomous Active)", Toast.LENGTH_SHORT).show()
            } else {
                btnAutoToggleRun.text = "▶ START"
                btnAutoToggleRun.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_green))
                udpClient.sendCommand("STOP", 0)
                Toast.makeText(this, "Mission on STANDBY (Motors Stopped)", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun updateModeUi(mode: ControlMode) {
        runOnUiThread {
            when (mode) {
                ControlMode.MANUAL -> {
                    isAutonomousRunning = false
                    btnAutoToggleRun.visibility = View.GONE
                    tvModeIndicator.text = "[MODE: MANUAL]"
                    tvModeIndicator.setTextColor(ContextCompat.getColor(this, R.color.hud_orange))
                    tvCurrentAction.text = "ACTION: MANUAL CONTROLLER ACTIVE"
                    tvCurrentAction.setTextColor(ContextCompat.getColor(this, R.color.hud_orange))
                    btnManualMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_orange))
                    btnAutoMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_gray))
                }
                ControlMode.AUTONOMOUS -> {
                    isAutonomousRunning = false
                    btnAutoToggleRun.visibility = View.VISIBLE
                    btnAutoToggleRun.text = "▶ START"
                    btnAutoToggleRun.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_green))
                    tvModeIndicator.text = "[MODE: AUTONOMOUS AI]"
                    tvModeIndicator.setTextColor(ContextCompat.getColor(this, R.color.hud_cyan))
                    tvCurrentAction.text = "AUTO: [STANDBY - MOTORS OFF] TAP START TO DRIVE"
                    tvCurrentAction.setTextColor(ContextCompat.getColor(this, R.color.hud_yellow))
                    btnAutoMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_cyan))
                    btnManualMode.setBackgroundColor(ContextCompat.getColor(this, R.color.hud_gray))
                    udpClient.sendCommand("STOP", 0)
                }
                ControlMode.EMERGENCY_STOP -> {
                    isAutonomousRunning = false
                    btnAutoToggleRun.visibility = View.GONE
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

    override fun onControllerInput(
        axisX: Float,
        axisY: Float,
        rightTrigger: Float,
        leftTrigger: Float,
        turboBoost: Boolean
    ) {
        lastAxisX = axisX
        lastAxisY = axisY
        lastRt = rightTrigger
        lastLt = leftTrigger
        lastTurbo = turboBoost

        if (!modeManager.isManual()) return

        // 1. ADAS Active Safety (Auto Emergency Braking in Manual Mode)
        // If driver is attempting forward throttle (RT > 0.03 or Stick Y < -0.05) AND obstacle is right ahead
        val isTryingForward = (rightTrigger > 0.03f) || (axisY < -0.05f)
        val aebEngaged = isTryingForward && isForwardObstacleHazard

        if (aebEngaged) {
            differentialDrive.reset()
            udpClient.sendDriveCommand(0, 0)
            triggerHapticAlert()

            runOnUiThread {
                tvMotorOutputs.text = "MOTORS: 0 | 0 PWM [⚠️ ADAS AEB BRAKE ACTIVE]"
                tvCurrentAction.text = "⚠️ OBSTACLE (${hazardName.uppercase()}) DETECTED! RELEASE THROTTLE OR REVERSE"
                tvCurrentAction.setTextColor(ContextCompat.getColor(this, R.color.hud_red))
            }
            return
        }

        // 2. High-Performance Proportional Driving (RT=Gas, LT=Brake/Rev, StickX=Steering)
        val outputs = differentialDrive.computeMotorOutputs(
            stickX = axisX,
            stickY = axisY,
            rightTrigger = rightTrigger,
            leftTrigger = leftTrigger,
            turboBoost = turboBoost,
            emergencyBrakeOverride = false
        )

        udpClient.sendDriveCommand(outputs.leftPwm, outputs.rightPwm)

        runOnUiThread {
            val turboTag = if (outputs.isTurboActive) " [🔥TURBO BOOST 1023]" else ""
            val cruiseTag = if (differentialDrive.isCruiseControlActive) " [CRUISE ON]" else ""
            val gasPct = (rightTrigger * 100).toInt()
            val revPct = (leftTrigger * 100).toInt()

            tvMotorOutputs.text = "MOTORS: L: ${outputs.leftPwm} | R: ${outputs.rightPwm} PWM$turboTag$cruiseTag"
            tvCurrentAction.text = "MANUAL: RT(Gas): $gasPct% | LT(Rev): $revPct% | Steer: ${"%.2f".format(axisX)}"
            tvCurrentAction.setTextColor(
                if (outputs.isTurboActive) ContextCompat.getColor(this, R.color.hud_orange)
                else ContextCompat.getColor(this, R.color.hud_cyan)
            )
        }
    }

    override fun onJoystickMoved(axisX: Float, axisY: Float) {
        onControllerInput(axisX, axisY, lastRt, lastLt, lastTurbo)
    }

    override fun onButtonActionTriggered(action: ControllerButtonAction) {
        when (action) {
            ControllerButtonAction.ENABLE_MANUAL -> {
                if (modeManager.isEmergencyStop()) {
                    modeManager.resetEmergencyStop(ControlMode.MANUAL)
                } else {
                    modeManager.setManualMode(aresController.isConnected(), "Gamepad Button A")
                }
                triggerHapticAlert()
            }
            ControllerButtonAction.ENABLE_AUTONOMOUS -> {
                if (modeManager.isEmergencyStop()) {
                    modeManager.resetEmergencyStop(ControlMode.AUTONOMOUS)
                } else {
                    modeManager.setAutonomousMode(isCameraPipelineReady, "Gamepad Button B")
                }
                triggerHapticAlert()
            }
            ControllerButtonAction.EMERGENCY_STOP -> {
                modeManager.triggerEmergencyStop("Gamepad Button X Pressed")
                triggerHapticAlert()
            }
            ControllerButtonAction.CYCLE_SPEED_PROFILE -> {
                val newProfile = differentialDrive.cycleSpeedProfile()
                updateProfileUi(newProfile)
                Toast.makeText(this, "Profile: ${newProfile.displayName}", Toast.LENGTH_SHORT).show()
                triggerHapticAlert()
            }
            ControllerButtonAction.TOGGLE_CRUISE_CONTROL -> {
                if (modeManager.isAutonomous()) {
                    toggleAutoRunStandby()
                } else {
                    val active = differentialDrive.toggleCruiseControl()
                    Toast.makeText(this, if (active) "Cruise Control ENGAGED [Speed Locked]" else "Cruise Control CANCELLED", Toast.LENGTH_SHORT).show()
                    triggerHapticAlert()
                }
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

    private fun triggerHapticAlert() {
        try {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                vibrator?.vibrate(android.os.VibrationEffect.createOneShot(120, android.os.VibrationEffect.DEFAULT_AMPLITUDE))
            } else {
                @Suppress("DEPRECATION")
                vibrator?.vibrate(120)
            }
        } catch (e: Exception) {
            // ignore if hardware doesn't support
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
            val targetRot = previewView.display?.rotation ?: Surface.ROTATION_90

            val preview = Preview.Builder()
                .setTargetRotation(targetRot)
                .build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }

            val imageAnalyzer = ImageAnalysis.Builder()
                .setTargetRotation(targetRot)
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

        // 2. Active Safety Obstacle & Collision Check (Continuous in Both Modes)
        // ONLY triggers for actual stop/blocking hazards, never for turning signs
        val hazardSign = detections.firstOrNull { det ->
            (det.className in listOf("stop", "no_entry", "dead_end") && det.heightRatio >= 0.08f)
        }

        if (hazardSign != null) {
            isForwardObstacleHazard = true
            hazardName = hazardSign.className
            if (modeManager.isManual() && (lastRt > 0.03f || lastAxisY < -0.05f)) {
                // Slam emergency brake in manual mode to prevent forward crash
                differentialDrive.reset()
                udpClient.sendDriveCommand(0, 0)
                triggerHapticAlert()
            }
        } else {
            isForwardObstacleHazard = false
            hazardName = "CLEAR"
        }

        // 3. Evaluate Autonomous Decision Engine
        val isAutonomous = modeManager.isAutonomous()
        val decision = decisionEngine.processDetections(detections, manualOverride = !isAutonomous)

        // 4. Dispatch Wireless UDP Command ONLY when in Autonomous Mode
        if (isAutonomous) {
            if (isAutonomousRunning) {
                udpClient.sendCommand(decision.command, decision.speed)
            } else {
                udpClient.sendCommand("STOP", 0)
            }
        }

        // 5. Update Cockpit HUD on UI Thread
        val now = System.currentTimeMillis()
        val fps = 1000f / maxOf(1f, (now - lastFrameTime).toFloat())
        lastFrameTime = now

        runOnUiThread {
            overlayView.setResults(detections, decision)
            tvFps.text = "FPS: ${"%.1f".format(fps)}"
            val orientDesc = when (manualRotationOffset) {
                0 -> "0° [UPRIGHT]"
                90 -> "90° [PORTRAIT]"
                180 -> "180° [REV-LAND]"
                270 -> "270° [INVERTED]"
                else -> "${manualRotationOffset}°"
            }
            tvInference.text = "AI: ${dtInference}ms | ORIENT: $orientDesc [Tap]"

            val pingText = if (udpClient.isConnected) "${udpClient.lastPingMs}ms" else "DISCONNECTED"
            tvCarStatus.text = "CAR UDP: $pingText"

            if (isAutonomous) {
                if (isAutonomousRunning) {
                    tvCurrentAction.text = "AUTO ACTIVE: ${decision.statusMessage}"
                    tvSignInfo.text = "TARGET: ${decision.targetSignName.uppercase()} | ZONE: ${decision.distanceZone}"
                    tvMotorOutputs.text = "AUTO MOTOR: ${decision.command} @ ${decision.speed} PWM"
                    tvCurrentAction.setTextColor(
                        if (decision.command == "STOP") ContextCompat.getColor(this, R.color.hud_red)
                        else ContextCompat.getColor(this, R.color.hud_cyan)
                    )
                } else {
                    tvCurrentAction.text = "AUTO: [STANDBY - MOTORS OFF] TAP START TO DRIVE"
                    val detectedText = if (detections.isNotEmpty()) "${detections[0].className.uppercase()} (${(detections[0].confidence*100).toInt()}%)" else "ROAD CLEAR"
                    tvSignInfo.text = "VISION: $detectedText | TARGET: ${decision.targetSignName.uppercase()} (READY)"
                    tvMotorOutputs.text = "AUTO MOTOR: STANDBY (0 PWM)"
                    tvCurrentAction.setTextColor(ContextCompat.getColor(this, R.color.hud_yellow))
                }
            } else if (modeManager.isManual()) {
                val detectedText = if (detections.isNotEmpty()) "${detections[0].className.uppercase()} (${(detections[0].confidence*100).toInt()}%)" else "ROAD CLEAR"
                val radarStatus = if (isForwardObstacleHazard) " [⚠️ COLLISION WARNING: $hazardName]" else " [ADAS: SAFE]"
                tvSignInfo.text = "VISION: $detectedText$radarStatus"
            }
        }
    }

    @androidx.annotation.OptIn(androidx.camera.core.ExperimentalGetImage::class)
    private fun imageProxyToBitmap(imageProxy: ImageProxy): Bitmap? {
        val totalRotation = (imageProxy.imageInfo.rotationDegrees + manualRotationOffset) % 360
        return try {
            val bmp = imageProxy.toBitmap()
            if (totalRotation != 0) {
                val matrix = Matrix().apply { postRotate(totalRotation.toFloat()) }
                Bitmap.createBitmap(bmp, 0, 0, bmp.width, bmp.height, matrix, true)
            } else {
                bmp
            }
        } catch (e: Throwable) {
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

            if (totalRotation != 0) {
                val matrix = Matrix().apply { postRotate(totalRotation.toFloat()) }
                Bitmap.createBitmap(bitmap, 0, 0, image.width, image.height, matrix, true)
            } else {
                bitmap
            }
        }
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
