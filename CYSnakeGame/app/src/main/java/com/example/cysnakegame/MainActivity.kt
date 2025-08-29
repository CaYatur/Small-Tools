package com.example.cysnakegame

import android.os.Bundle
import android.view.MotionEvent
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.wear.compose.material.Text
import kotlinx.coroutines.delay
import kotlin.math.min
import kotlin.random.Random

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SnakeGame()
        }
    }
}

data class Position(val x: Int, val y: Int)

enum class Direction {
    UP, DOWN, LEFT, RIGHT
}

@Composable
fun SnakeGame() {
    var snake by remember { mutableStateOf(listOf(Position(5, 5))) }
    var direction by remember { mutableStateOf(Direction.RIGHT) }
    var apple by remember { mutableStateOf(Position(10, 10)) }
    var score by remember { mutableStateOf(0) }
    var time by remember { mutableStateOf(0) }
    var isPlaying by remember { mutableStateOf(false) }
    var isGameOver by remember { mutableStateOf(false) }

    val textMeasurer = rememberTextMeasurer()

    // Oyun döngüsü - daha güvenilir
    LaunchedEffect(isPlaying, isGameOver) {
        while (isPlaying && !isGameOver) {
            delay(200) // Oyun hızı
            
            // Yılanı hareket ettir
            val head = snake.first()
            val newHead = when (direction) {
                Direction.UP -> Position(head.x, head.y - 1)
                Direction.DOWN -> Position(head.x, head.y + 1)
                Direction.LEFT -> Position(head.x - 1, head.y)
                Direction.RIGHT -> Position(head.x + 1, head.y)
            }

            // Duvar çarpışması - karşıya ışınla
            val gridSize = 20
            val wrappedHead = Position(
                (newHead.x + gridSize) % gridSize,
                (newHead.y + gridSize) % gridSize
            )

            // Kendine çarpma kontrolü
            if (wrappedHead in snake) {
                isGameOver = true
                continue
            }

            val newSnake = listOf(wrappedHead) + snake

            // Elma yeme
            if (wrappedHead == apple) {
                score++
                apple = generateApple(newSnake, gridSize)
                snake = newSnake // Elma yendi, yılan büyür
            } else {
                snake = newSnake.dropLast(1) // Elma yemedi, yılan aynı boyutta kalır
            }
        }
    }

    // Zaman sayacı - gerçek saniye
    LaunchedEffect(isPlaying, isGameOver) {
        while (isPlaying && !isGameOver) {
            delay(1000) // 1 saniye
            time++
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = {
                        if (!isPlaying) {
                            // Oyunu başlat
                            isPlaying = true
                            isGameOver = false
                            snake = listOf(Position(5, 5))
                            direction = Direction.RIGHT
                            apple = Position(10, 10)
                            score = 0
                            time = 0
                        } else if (isGameOver) {
                            // Yeniden başlat
                            isGameOver = false
                            snake = listOf(Position(5, 5))
                            direction = Direction.RIGHT
                            apple = Position(10, 10)
                            score = 0
                            time = 0
                        } else {
                            // Yön değiştir
                            val centerX = size.width / 2f
                            val centerY = size.height / 2f
                            val tapX = it.x
                            val tapY = it.y

                            val deltaX = tapX - centerX
                            val deltaY = tapY - centerY

                            direction = when {
                                kotlin.math.abs(deltaX) > kotlin.math.abs(deltaY) -> {
                                    if (deltaX > 0) Direction.RIGHT else Direction.LEFT
                                }
                                else -> {
                                    if (deltaY > 0) Direction.DOWN else Direction.UP
                                }
                            }
                        }
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val canvasWidth = size.width
            val canvasHeight = size.height
            val radius = min(canvasWidth, canvasHeight) / 2
            val centerX = canvasWidth / 2
            val centerY = canvasHeight / 2

            // Yuvarlak ızgara oluştur
            val gridSize = 20
            val cellSize = radius * 2 / gridSize

            // Arka plan siyah
            drawCircle(Color.Black, radius, Offset(centerX, centerY))

            if (!isPlaying && !isGameOver) {
                // Başlangıç ekranı
                val startText = "Başlamak için Dokunun"
                val textLayoutResult = textMeasurer.measure(startText, TextStyle(fontSize = 16.sp, color = Color.White))
                drawText(
                    textLayoutResult,
                    topLeft = Offset(centerX - textLayoutResult.size.width / 2, centerY - textLayoutResult.size.height / 2)
                )
            } else {
                // Yılanı çiz (yeşil)
                snake.forEach { pos ->
                    val x = centerX + (pos.x - gridSize / 2) * cellSize
                    val y = centerY + (pos.y - gridSize / 2) * cellSize
                    drawCircle(Color.Green, cellSize / 2, Offset(x, y))
                }

                // Elmayı çiz (kırmızı)
                val appleX = centerX + (apple.x - gridSize / 2) * cellSize
                val appleY = centerY + (apple.y - gridSize / 2) * cellSize
                drawCircle(Color.Red, cellSize / 2, Offset(appleX, appleY))

                // Skor ve süre - yuvarlak ekrana göre ayarlandı
                val scoreText = "Puan: $score"
                val timeText = "Süre: $time"
                val scoreLayout = textMeasurer.measure(scoreText, TextStyle(fontSize = 14.sp, color = Color.Yellow))
                val timeLayout = textMeasurer.measure(timeText, TextStyle(fontSize = 14.sp, color = Color.Cyan))

                // Üst merkez
                drawText(scoreLayout, topLeft = Offset(centerX - scoreLayout.size.width / 2, 20f))
                // Alt merkez
                drawText(timeLayout, topLeft = Offset(centerX - timeLayout.size.width / 2, canvasHeight - timeLayout.size.height - 20f))

                if (isGameOver) {
                    val gameOverText = "Oyun Bitti\nYeniden Başlamak için Dokunun"
                    val gameOverLayout = textMeasurer.measure(gameOverText, TextStyle(fontSize = 16.sp, color = Color.Red))
                    drawText(
                        gameOverLayout,
                        topLeft = Offset(centerX - gameOverLayout.size.width / 2, centerY - gameOverLayout.size.height / 2)
                    )
                }
            }
        }
    }
}

fun generateApple(snake: List<Position>, gridSize: Int): Position {
    var apple: Position
    do {
        apple = Position(Random.nextInt(gridSize), Random.nextInt(gridSize))
    } while (apple in snake)
    return apple
}
