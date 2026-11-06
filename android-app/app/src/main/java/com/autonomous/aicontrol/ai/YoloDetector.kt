package com.autonomous.aicontrol.ai

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import android.content.Context
import android.graphics.Bitmap
import android.graphics.RectF
import android.util.Log
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.FloatBuffer
import java.util.Collections
import kotlin.math.max
import kotlin.math.min

class YoloDetector(
    private val context: Context,
    private val modelFileName: String = "yolov8n.onnx",
    private val confThreshold: Float = 0.35f,
    private val iouThreshold: Float = 0.45f
) : AutoCloseable {

    companion object {
        private const val TAG = "YoloDetector"
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

    private val ortEnv = OrtEnvironment.getEnvironment()
    private var session: OrtSession? = null
    private var inputName: String = "images"

    // Direct FloatBuffer for 1 * 3 * 640 * 640 floats in native byte order
    private val inputBuffer: FloatBuffer = ByteBuffer.allocateDirect(1 * 3 * INPUT_SIZE * INPUT_SIZE * 4)
        .order(ByteOrder.nativeOrder())
        .asFloatBuffer()

    private val intValues = IntArray(INPUT_SIZE * INPUT_SIZE)

    init {
        loadModel()
    }

    private fun loadModel() {
        try {
            val sessionOptions = OrtSession.SessionOptions().apply {
                setIntraOpNumThreads(4)
                setOptimizationLevel(OrtSession.SessionOptions.OptLevel.ALL_OPT)
            }
            val modelBytes = context.assets.open(modelFileName).use { it.readBytes() }
            session = ortEnv.createSession(modelBytes, sessionOptions)
            inputName = session?.inputNames?.iterator()?.next() ?: "images"
            Log.i(TAG, "YOLOv8 ONNX model loaded successfully from assets/$modelFileName (inputName=$inputName)")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load ONNX model from assets/$modelFileName", e)
        }
    }

    fun isReady(): Boolean = session != null

    fun detect(bitmap: Bitmap): List<DetectionResult> {
        val ortSession = session ?: run {
            Log.w(TAG, "ONNX Session is null, cannot detect")
            return emptyList()
        }

        // 1. Preprocess: Resize to 640x640 and extract RGB
        val scaledBitmap = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true)
        scaledBitmap.getPixels(intValues, 0, INPUT_SIZE, 0, 0, INPUT_SIZE, INPUT_SIZE)

        val numPixels = INPUT_SIZE * INPUT_SIZE
        inputBuffer.rewind()

        // CHW Layout: R channel, then G channel, then B channel
        for (i in 0 until numPixels) {
            inputBuffer.put(((intValues[i] shr 16) and 0xFF) / 255.0f)
        }
        for (i in 0 until numPixels) {
            inputBuffer.put(((intValues[i] shr 8) and 0xFF) / 255.0f)
        }
        for (i in 0 until numPixels) {
            inputBuffer.put((intValues[i] and 0xFF) / 255.0f)
        }
        inputBuffer.rewind()

        // 2. Inference Forward Pass
        val shape = longArrayOf(1, 3, INPUT_SIZE.toLong(), INPUT_SIZE.toLong())
        val tensor = OnnxTensor.createTensor(ortEnv, inputBuffer, shape)

        val results = try {
            ortSession.run(Collections.singletonMap(inputName, tensor))
        } catch (e: Exception) {
            Log.e(TAG, "Inference run error", e)
            tensor.close()
            return emptyList()
        }
        tensor.close()

        val outputTensor = results.get(0) as? OnnxTensor ?: run {
            results.close()
            return emptyList()
        }

        // 3. Postprocess Output Tensor [1, 10, 8400]
        val candidates = mutableListOf<DetectionResult>()
        val rawValue = outputTensor.value

        if (rawValue is Array<*> && rawValue.isNotEmpty() && rawValue[0] is Array<*>) {
            @Suppress("UNCHECKED_CAST")
            val preds = rawValue[0] as Array<FloatArray>
            for (i in 0 until 8400) {
                var maxScore = 0.0f
                var maxClass = -1
                for (c in 0 until 6) {
                    val score = preds[4 + c][i]
                    if (score > maxScore) {
                        maxScore = score
                        maxClass = c
                    }
                }

                if (maxScore >= confThreshold && maxClass != -1) {
                    val cx = preds[0][i] / INPUT_SIZE.toFloat()
                    val cy = preds[1][i] / INPUT_SIZE.toFloat()
                    val w = preds[2][i] / INPUT_SIZE.toFloat()
                    val h = preds[3][i] / INPUT_SIZE.toFloat()

                    val left = max(0.0f, cx - w / 2.0f)
                    val top = max(0.0f, cy - h / 2.0f)
                    val right = min(1.0f, cx + w / 2.0f)
                    val bottom = min(1.0f, cy + h / 2.0f)

                    val boxW = right - left
                    val boxH = bottom - top
                    val areaRatio = boxW * boxH

                    val aspect = if (boxH > 0f) boxW / boxH else 0f
                    if (areaRatio in 0.002f..0.95f && aspect in 0.30f..3.0f) {
                        candidates.add(
                            DetectionResult(
                                classId = maxClass,
                                className = CLASS_NAMES[maxClass],
                                confidence = maxScore,
                                box = RectF(left, top, right, bottom),
                                areaRatio = areaRatio,
                                heightRatio = boxH
                            )
                        )
                    }
                }
            }
        } else {
            val fb = outputTensor.floatBuffer
            val numBoxes = 8400
            for (i in 0 until numBoxes) {
                var maxScore = 0.0f
                var maxClass = -1
                for (c in 0 until 6) {
                    val score = fb.get((4 + c) * numBoxes + i)
                    if (score > maxScore) {
                        maxScore = score
                        maxClass = c
                    }
                }

                if (maxScore >= confThreshold && maxClass != -1) {
                    val cx = fb.get(0 * numBoxes + i) / INPUT_SIZE.toFloat()
                    val cy = fb.get(1 * numBoxes + i) / INPUT_SIZE.toFloat()
                    val w = fb.get(2 * numBoxes + i) / INPUT_SIZE.toFloat()
                    val h = fb.get(3 * numBoxes + i) / INPUT_SIZE.toFloat()

                    val left = max(0.0f, cx - w / 2.0f)
                    val top = max(0.0f, cy - h / 2.0f)
                    val right = min(1.0f, cx + w / 2.0f)
                    val bottom = min(1.0f, cy + h / 2.0f)

                    val boxW = right - left
                    val boxH = bottom - top
                    val areaRatio = boxW * boxH

                    val aspect = if (boxH > 0f) boxW / boxH else 0f
                    if (areaRatio in 0.002f..0.95f && aspect in 0.30f..3.0f) {
                        candidates.add(
                            DetectionResult(
                                classId = maxClass,
                                className = CLASS_NAMES[maxClass],
                                confidence = maxScore,
                                box = RectF(left, top, right, bottom),
                                areaRatio = areaRatio,
                                heightRatio = boxH
                            )
                        )
                    }
                }
            }
        }

        outputTensor.close()
        results.close()

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
        return if (unionArea > 0f) interArea / unionArea else 0f
    }

    override fun close() {
        try {
            session?.close()
            ortEnv.close()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
