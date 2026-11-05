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
    private var sequenceNumber = 0L

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var heartbeatJob: Job? = null

    var lastPingMs: Long = -1L
        private set
    var isConnected: Boolean = false
        private set
    var currentTrim: Int = 0

    private var lastSentAction = "STOP"
    private var lastSentSpeed = 700

    init {
        try {
            socket = DatagramSocket()
            socket?.soTimeout = 200
            inetAddress = InetAddress.getByName(espIpAddress)
            startHeartbeatAndReceiver()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun sendCommand(action: String, speed: Int = lastSentSpeed, trim: Int = currentTrim) {
        lastSentAction = action.uppercase()
        lastSentSpeed = speed
        currentTrim = trim

        scope.launch {
            transmitPacket(lastSentAction, lastSentSpeed, currentTrim)
        }
    }

    private fun transmitPacket(action: String, speed: Int, trim: Int) {
        val s = socket ?: return
        val addr = inetAddress ?: return

        try {
            sequenceNumber++
            val payload = "CMD:$action:$speed:$trim:$sequenceNumber\n"
            val data = payload.toByteArray(Charsets.UTF_8)
            val packet = DatagramPacket(data, data.size, addr, port)
            val t0 = System.currentTimeMillis()
            s.send(packet)
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
                    // Send periodic heartbeat every 250ms to keep ESP8266 watchdog fed
                    transmitPacket(lastSentAction, lastSentSpeed, currentTrim)

                    val t0 = System.currentTimeMillis()
                    socket?.receive(receivePacket)
                    lastPingMs = System.currentTimeMillis() - t0
                    isConnected = true
                } catch (e: Exception) {
                    // Timeout or dropped packet
                    lastPingMs = -1L
                }
                delay(200L)
            }
        }
    }

    fun emergencyStop() {
        lastSentAction = "STOP"
        lastSentSpeed = 0
        scope.launch {
            // Burst 3 STOP packets to guarantee delivery through wireless packet loss
            repeat(3) {
                transmitPacket("STOP", 0, currentTrim)
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
