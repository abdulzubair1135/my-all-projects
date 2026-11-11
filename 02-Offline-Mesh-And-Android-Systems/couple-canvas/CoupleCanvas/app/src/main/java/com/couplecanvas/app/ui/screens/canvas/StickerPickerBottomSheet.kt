package com.couplecanvas.app.ui.screens.canvas

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplecanvas.app.ui.theme.RosePrimary

data class StickerItem(
    val id: String,
    val emoji: String,
    val name: String,
    val category: String
)

val CoupleStickers = listOf(
    StickerItem("heart_rose", "❤️", "Red Heart", "Hearts"),
    StickerItem("heart_sparkle", "💖", "Sparkle Heart", "Hearts"),
    StickerItem("heart_two", "💕", "Two Hearts", "Hearts"),
    StickerItem("rose", "🌹", "Rose", "Flowers"),
    StickerItem("flower_cherry", "🌸", "Cherry Blossom", "Flowers"),
    StickerItem("star", "⭐", "Gold Star", "Stars"),
    StickerItem("sparkles", "✨", "Sparkles", "Stars"),
    StickerItem("bear", "🧸", "Teddy Bear", "Animals"),
    StickerItem("cat_love", "😻", "Love Cat", "Animals"),
    StickerItem("cake", "🎂", "Cake", "Celebration"),
    StickerItem("cupcake", "🧁", "Cupcake", "Food"),
    StickerItem("sunset", "🌅", "Sunset", "Travel"),
    StickerItem("love_letter", "💌", "Love Letter", "Love")
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StickerPickerBottomSheet(
    onDismissRequest: () -> Unit,
    onStickerSelected: (assetId: String, category: String) -> Unit
) {
    val sheetState = rememberModalBottomSheetState()
    val categories = listOf("All", "Hearts", "Flowers", "Stars", "Animals", "Love")
    var selectedCategoryIndex by remember { mutableStateOf(0) }

    val filteredStickers = remember(selectedCategoryIndex) {
        val cat = categories[selectedCategoryIndex]
        if (cat == "All") CoupleStickers else CoupleStickers.filter { it.category == cat }
    }

    ModalBottomSheet(
        onDismissRequest = onDismissRequest,
        sheetState = sheetState
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Choose a Couple Sticker 💕",
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold
                ),
                modifier = Modifier.padding(bottom = 12.dp)
            )

            ScrollableTabRow(
                selectedTabIndex = selectedCategoryIndex,
                edgePadding = 0.dp,
                modifier = Modifier.fillMaxWidth()
            ) {
                categories.forEachIndexed { index, catName ->
                    Tab(
                        selected = selectedCategoryIndex == index,
                        onClick = { selectedCategoryIndex = index },
                        text = { Text(catName, fontWeight = if (selectedCategoryIndex == index) FontWeight.Bold else FontWeight.Normal) }
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            LazyVerticalGrid(
                columns = GridCells.Fixed(4),
                contentPadding = PaddingValues(8.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                modifier = Modifier.height(260.dp)
            ) {
                items(filteredStickers) { item ->
                    Box(
                        modifier = Modifier
                            .size(64.dp)
                            .clip(RoundedCornerShape(16.dp))
                            .clickable {
                                onStickerSelected(item.id, item.category)
                                onDismissRequest()
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Text(text = item.emoji, fontSize = 36.sp)
                    }
                }
            }
        }
    }
}
