package com.autonomous.aicontrol.ai

import android.content.Context
import android.graphics.Bitmap
import android.graphics.RectF
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.CompatibilityList
import org.tensorflow.lite.gpu.GpuDelegate
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.math.max
import kotlin.math.min

class YoloDetector(
    private val context: Context,
    private val modelFileName: String = "yolov8n.tflite",
    private val confThreshold: Float = 0.60f,
    private val iouThreshold: Float = 0.45f
) {
    companion object {
        const val INPUT_SIZE = 640
        val CLASS_NAMES = arrayOf(
            "left_turn",        // 0
            "straight_ahead",   // 1
            "right_turn",       // 2
            "dead_end",         // 3
            "no_entry",         // 4
            "stop"              // 5
        )
    }

    private var interpreter: Interpreter? = null
    private var gpuDelegate: GpuDelegate? = null
    private val inputBuffer = ByteBuffer.allocateDirect(1 * 3 * INPUT_SIZE * INPUT_SIZE * 4).apply {
        order(ByteOrder.nativeOrder())
    }

    // Output tensor: [1, 10, 8400]
    private val outputBuffer = Array(1) { Array(10) { FloatArray(8400) } }

    init {
        loadModel()
    }

    private fun loadModel() {
        val options = Interpreter.Options()
        try {
            val compatList = CompatibilityList()
            if (compatList.isDelegateSupportedOnThisDevice) {
                gpuDelegate = GpuDelegate()
                options.addDelegate(gpuDelegate)
            } else {
                options.setNumThreads(4)
            }
        } catch (e: Throwable) {
            options.setNumThreads(4)
        }

        try {
            val modelBuffer = loadModelFile(modelFileName)
            interpreter = Interpreter(modelBuffer, options)
        } catch (e: Exception) {
            e.printStackTrace()
            // Fallback to CPU with 4 threads
            val cpuOptions = Interpreter.Options().apply { setNumThreads(4) }
            interpreter = Interpreter(loadModelFile(modelFileName), cpuOptions)
        }
    }

    private fun loadModelFile(fileName: String): MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(fileName)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

    fun detect(bitmap: Bitmap): List<DetectionResult> {
        val tflite = interpreter ?: return emptyList()

        // 1. Preprocess: Resize to 640x640 and normalize to [0.0, 1.0]
        val scaledBitmap = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true)
        inputBuffer.rewind()

        val intValues = IntArray(INPUT_SIZE * INPUT_SIZE)
        scaledBitmap.getPixels(intValues, 0, INPUT_SIZE, 0, 0, INPUT_SIZE, INPUT_SIZE)

        // CHW Layout: R channel then G channel then B channel
        for (c in 0 until 3) {
            for (i in intValues.indices) {
                val pixel = intValues[i]
                val channelValue = when (c) {
                    0 -> ((pixel shr 16) and 0xFF) / 255.0f // R
                    1 -> ((pixel shr 8) and 0xFF) / 255.0f  // G
                    else -> (pixel and 0xFF) / 255.0f       // B
                }
                inputBuffer.putFloat(channelValue)
            }
        }

        // 2. Inference Forward Pass
        tflite.run(inputBuffer, outputBuffer)

        // 3. Postprocess Output Tensor [1, 10, 8400]
        val candidates = mutableListOf<DetectionResult>()
        val predictions = outputBuffer[0] // 10 rows, 8400 columns

        for (i in 0 until 8400) {
            var maxProb = 0.0f
            var maxClassId = -1

            for (c in 0 until 6) {
                val prob = predictions[4 + c][i]
                if (prob > maxProb) {
                    maxProb = prob
                    maxClassId = c
                }
            }

            if (maxProb >= confThreshold && maxClassId != -1) {
                val cx = predictions[0][i] / INPUT_SIZE
                val cy = predictions[1][i] / INPUT_SIZE
                val w = predictions[2][i] / INPUT_SIZE
                val h = predictions[3][i] / INPUT_SIZE

                val left = max(0.0f, cx - w / 2.0f)
                val top = max(0.0f, cy - h / 2.0f)
                val right = min(1.0f, cx + w / 2.0f)
                val bottom = min(1.0f, cy + h / 2.0f)

                val boxW = right - left
                val boxH = bottom - top
                val areaRatio = boxW * boxH

                // Geometric verification filter
                val aspect = if (boxH > 0) boxW / boxH else 0f
                if (areaRatio in 0.003f..0.45f && aspect in 0.45f..2.2f) {
                    candidates.add(
                        DetectionResult(
                            classId = maxClassId,
                            className = CLASS_NAMES[maxClassId],
                            confidence = maxProb,
                            box = RectF(left, top, right, bottom),
                            areaRatio = areaRatio,
                            heightRatio = boxH
                        )
                    )
                }
            }
        }

        // 4. Non-Maximum Suppression (NMS)
        return applyNMS(candidates, iouThreshold)
    }

    private fun applyNMS(boxes: List<DetectionResult>, threshold: Float): List<DetectionResult> {
        val sorted = boxes.sortedByDescending { it.confidence }.toMutableList()
        val selected = mutableListOf<DetectionResult>()

        while (sorted.isNotEmpty()) {
            val first = sorted.removeAt(0)
            selected.add(first)

            val iterator = sorted.iterator()
            while (iterator.hasNext()) {
                val next = iterator.next()
                if (calculateIoU(first.box, next.box) >= threshold) {
                    iterator.remove()
                }
            }
        }
        return selected
    }

    private fun calculateIoU(a: RectF, b: RectF): Float {
        val interLeft = max(a.left, b.left)
        val interTop = max(a.top, b.top)
        val interRight = min(a.right, b.right)
        val interBottom = min(a.bottom, b.bottom)

        val interArea = max(0f, interRight - interLeft) * max(0f, interBottom - interTop)
        val unionArea = (a.width() * a.height()) + (b.width() * b.height()) - interArea
        return if (unionArea > 0) interArea / unionArea else 0f
    }

    fun close() {
        interpreter?.close()
        gpuDelegate?.close()
    }
}
