package com.autonomous.aicontrol.ui

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.View
import com.autonomous.aicontrol.ai.DetectionResult
import com.autonomous.aicontrol.decision.DrivingDecision

class OverlayView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var detections: List<DetectionResult> = emptyList()
    private var decision: DrivingDecision? = null

    private val boxPaint = Paint().apply {
        style = Paint.Style.STROKE
        strokeWidth = 6f
        isAntiAlias = true
    }

    private val cornerPaint = Paint().apply {
        style = Paint.Style.STROKE
        strokeWidth = 8f
        color = Color.CYAN
        isAntiAlias = true
    }

    private val textBgPaint = Paint().apply {
        style = Paint.Style.FILL
        isAntiAlias = true
    }

    private val textPaint = Paint().apply {
        color = Color.BLACK
        textSize = 34f
        typeface = Typeface.create(Typeface.MONOSPACE, Typeface.BOLD)
        isAntiAlias = true
    }

    fun setResults(detections: List<DetectionResult>, decision: DrivingDecision) {
        this.detections = detections
        this.decision = decision
        postInvalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val w = width.toFloat()
        val h = height.toFloat()

        // 1. Draw Bounding Boxes
        for (det in detections) {
            val rect = det.box
            val left = rect.left * w
            val top = rect.top * h
            val right = rect.right * w
            val bottom = rect.bottom * h

            val color = getColorForClass(det.classId)
            boxPaint.color = color
            textBgPaint.color = color

            // Draw Box
            canvas.drawRect(left, top, right, bottom, boxPaint)

            // Draw Corner Brackets
            val cornerLen = 24f
            canvas.drawLine(left, top, left + cornerLen, top, cornerPaint)
            canvas.drawLine(left, top, left, top + cornerLen, cornerPaint)
            canvas.drawLine(right, bottom, right - cornerLen, bottom, cornerPaint)
            canvas.drawLine(right, bottom, right, bottom - cornerLen, cornerPaint)

            // Draw Badge
            val label = "${det.className.uppercase()} ${(det.confidence * 100).toInt()}%"
            val textWidth = textPaint.measureText(label)
            val badgeHeight = 44f
            val badgeTop = (top - badgeHeight).coerceAtLeast(0f)

            canvas.drawRect(left, badgeTop, left + textWidth + 16f, badgeTop + badgeHeight, textBgPaint)
            canvas.drawText(label, left + 8f, badgeTop + 32f, textPaint)
        }
    }

    private fun getColorForClass(classId: Int): Int {
        return when (classId) {
            0 -> Color.parseColor("#00E5FF") // Left Turn: Cyan
            1 -> Color.parseColor("#00E676") // Straight Ahead: Green
            2 -> Color.parseColor("#FF9100") // Right Turn: Orange
            3 -> Color.parseColor("#FFD600") // Dead End: Yellow
            4 -> Color.parseColor("#FF3D00") // No Entry: Orange-Red
            5 -> Color.parseColor("#FF1744") // Stop: Red
            else -> Color.GREEN
        }
    }
}
