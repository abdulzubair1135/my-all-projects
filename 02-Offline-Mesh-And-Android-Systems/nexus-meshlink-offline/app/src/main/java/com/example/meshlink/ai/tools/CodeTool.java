package com.example.meshlink.ai.tools;

public class CodeTool {

    public static ToolResult handleCodeRequest(String prompt) {
        String lower = prompt.toLowerCase();
        StringBuilder sb = new StringBuilder();

        if (lower.contains("factorial")) {
            sb.append("💻 **Factorial Function (Java):**\n\n");
            sb.append("```java\n");
            sb.append("public class MathUtils {\n");
            sb.append("    // Recursive factorial with guard\n");
            sb.append("    public static long factorial(int n) {\n");
            sb.append("        if (n <= 1) return 1;\n");
            sb.append("        return n * factorial(n - 1);\n");
            sb.append("    }\n");
            sb.append("}\n");
            sb.append("```\n\n");
            sb.append("• Time Complexity: `O(n)`\n");
            sb.append("• Space Complexity: `O(n)` call-stack space.");
            return ToolResult.text(sb.toString());
        }

        if (lower.contains("fibonacci")) {
            sb.append("💻 **Fibonacci Series (Java - Fast Iterative):**\n\n");
            sb.append("```java\n");
            sb.append("public static void printFibonacci(int count) {\n");
            sb.append("    long a = 0, b = 1;\n");
            sb.append("    for (int i = 0; i < count; i++) {\n");
            sb.append("        System.out.print(a + \" \");\n");
            sb.append("        long next = a + b;\n");
            sb.append("        a = b;\n");
            sb.append("        b = next;\n");
            sb.append("    }\n");
            sb.append("}\n");
            sb.append("```\n\n");
            sb.append("• `O(n)` Time, `O(1)` Space - zero stack overflow risk!");
            return ToolResult.text(sb.toString());
        }

        if (lower.contains("binary search")) {
            sb.append("💻 **Binary Search Implementation (Java):**\n\n");
            sb.append("```java\n");
            sb.append("public static int binarySearch(int[] arr, int target) {\n");
            sb.append("    int low = 0, high = arr.length - 1;\n");
            sb.append("    while (low <= high) {\n");
            sb.append("        int mid = low + (high - low) / 2;\n");
            sb.append("        if (arr[mid] == target) return mid;\n");
            sb.append("        if (arr[mid] < target) low = mid + 1;\n");
            sb.append("        else high = mid - 1;\n");
            sb.append("    }\n");
            sb.append("    return -1;\n");
            sb.append("}\n");
            sb.append("```\n\n");
            sb.append("• Shart: Array sorted hona zaroori hai. Time Complexity: `O(log n)`.");
            return ToolResult.text(sb.toString());
        }

        if (lower.contains("reverse string") || lower.contains("string reverse")) {
            sb.append("💻 **Reverse String in Java:**\n\n");
            sb.append("```java\n");
            sb.append("public static String reverse(String input) {\n");
            sb.append("    if (input == null) return null;\n");
            sb.append("    return new StringBuilder(input).reverse().toString();\n");
            sb.append("}\n");
            sb.append("```");
            return ToolResult.text(sb.toString());
        }

        // Generic code assist reply
        sb.append("💻 **Code Assistant (Hinglish):**\n\n");
        sb.append("Aapka code request samajh gaya: \"").append(prompt).append("\"\n\n");
        sb.append("Kripya exact language specify karein (e.g. Java, Kotlin, Python, JavaScript) ya koi error snippet paste karein, mai turant fix karke explanation de dunga!");
        return ToolResult.text(sb.toString());
    }
}
