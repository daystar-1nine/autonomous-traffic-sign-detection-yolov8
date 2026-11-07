package com.autonomous.aicontrol.network

import kotlinx.coroutines.*
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

class UdpVehicleClient(
    private val espIpAddress: String = "192.168.4.1",
    private val port: Int = 8888
) {
    private var socket: DatagramSocket? = null
    private var inetAddress: InetAddress? = null
    private var broadcastAddress: InetAddress? = null
    private var sequenceNumber = 0L

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var heartbeatJob: Job? = null

    var lastPingMs: Long = -1L
        private set
    var isConnected: Boolean = false
        private set
    var currentTrim: Int = 0

    // Autonomous Mode Action State
    private var lastSentAction = "STOP"
    private var lastSentSpeed = 700

    // Manual Direct Drive State
    private var lastDriveLeft = 0
    private var lastDriveRight = 0
    private var isDirectDriveMode = false

    init {
        try {
            socket = DatagramSocket().apply { broadcast = true }
            socket?.soTimeout = 200
            inetAddress = InetAddress.getByName(espIpAddress)
            broadcastAddress = InetAddress.getByName("255.255.255.255")
            startHeartbeatAndReceiver()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    /**
     * Dispatches high-level autonomous sign action command.
     * Protocol: CMD:<ACTION>:<SPEED>:<TRIM>:<SEQ>\n
     */
    fun sendCommand(action: String, speed: Int = lastSentSpeed, trim: Int = currentTrim) {
        isDirectDriveMode = false
        lastSentAction = action.uppercase()
        lastSentSpeed = speed
        currentTrim = trim

        scope.launch {
            transmitActionPacket(lastSentAction, lastSentSpeed, currentTrim)
        }
    }

    /**
     * Dispatches low-level differential drive manual motor PWMs.
     * Protocol: CMD:DRIVE:<LEFT_PWM>:<RIGHT_PWM>:<SEQ>\n
     */
    fun sendDriveCommand(leftPwm: Int, rightPwm: Int) {
        isDirectDriveMode = true
        lastDriveLeft = leftPwm.coerceIn(-1023, 1023)
        lastDriveRight = rightPwm.coerceIn(-1023, 1023)

        scope.launch {
            transmitDrivePacket(lastDriveLeft, lastDriveRight)
        }
    }

    private fun transmitActionPacket(action: String, speed: Int, trim: Int) {
        val s = socket ?: return
        val addr = inetAddress ?: return

        try {
            sequenceNumber++
            val payload = "CMD:$action:$speed:$trim:$sequenceNumber\n"
            val data = payload.toByteArray(Charsets.UTF_8)
            val packet = DatagramPacket(data, data.size, addr, port)
            s.send(packet)
            broadcastAddress?.let { bAddr ->
                s.send(DatagramPacket(data, data.size, bAddr, port))
            }
            isConnected = true
        } catch (e: Exception) {
            isConnected = false
            e.printStackTrace()
        }
    }

    private fun transmitDrivePacket(leftPwm: Int, rightPwm: Int) {
        val s = socket ?: return
        val addr = inetAddress ?: return

        try {
            sequenceNumber++
            val payload = "CMD:DRIVE:$leftPwm:$rightPwm:$sequenceNumber\n"
            val data = payload.toByteArray(Charsets.UTF_8)
            val packet = DatagramPacket(data, data.size, addr, port)
            s.send(packet)
            broadcastAddress?.let { bAddr ->
                s.send(DatagramPacket(data, data.size, bAddr, port))
            }
            isConnected = true
        } catch (e: Exception) {
            isConnected = false
            e.printStackTrace()
        }
    }

    private fun startHeartbeatAndReceiver() {
        heartbeatJob = scope.launch {
            val receiveBuffer = ByteArray(128)
            val receivePacket = DatagramPacket(receiveBuffer, receiveBuffer.size)

            while (isActive) {
                try {
                    // Send periodic heartbeat packet every 200ms to keep ESP8266 watchdog fed
                    if (isDirectDriveMode) {
                        transmitDrivePacket(lastDriveLeft, lastDriveRight)
                    } else {
                        transmitActionPacket(lastSentAction, lastSentSpeed, currentTrim)
                    }

                    val t0 = System.currentTimeMillis()
                    socket?.receive(receivePacket)
                    lastPingMs = System.currentTimeMillis() - t0
                    isConnected = true
                } catch (e: Exception) {
                    lastPingMs = -1L
                }
                delay(200L)
            }
        }
    }

    fun emergencyStop() {
        lastSentAction = "STOP"
        lastSentSpeed = 0
        lastDriveLeft = 0
        lastDriveRight = 0
        isDirectDriveMode = false

        scope.launch {
            // Burst 3 STOP packets to guarantee delivery through wireless packet loss
            repeat(3) {
                transmitActionPacket("STOP", 0, currentTrim)
                transmitDrivePacket(0, 0)
                delay(20L)
            }
        }
    }

    fun close() {
        heartbeatJob?.cancel()
        emergencyStop()
        scope.launch {
            delay(100L)
            socket?.close()
        }
    }
}
