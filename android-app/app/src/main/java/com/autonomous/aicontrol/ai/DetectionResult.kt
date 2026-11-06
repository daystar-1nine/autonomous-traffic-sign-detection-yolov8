package com.autonomous.aicontrol.ai

import android.graphics.RectF

data class DetectionResult(
    val classId: Int,
    val className: String,
    val confidence: Float,
    val box: RectF, // Normalized coordinates [0.0, 1.0]
    val areaRatio: Float,
    val heightRatio: Float
)
