// Program to demonstrate try and catch

import java.util.Scanner;

class ExceptionDemo
{
    public static void main(String args[])
    {
        Scanner sc = new Scanner(System.in);

        int a,b,c;

        try
        {
            System.out.println("Enter two numbers:");
            a = sc.nextInt();
            b = sc.nextInt();

            c = a/b;   // may cause exception

            System.out.println("Result = " + c);
        }

        catch(ArithmeticException e)
        {
            System.out.println("Error: Division by zero is not allowed");
        }

        System.out.println("Program continues...");
    }
}
