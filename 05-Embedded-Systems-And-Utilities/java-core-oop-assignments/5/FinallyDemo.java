// Program to demonstrate finally block

class FinallyDemo
{
    public static void main(String args[])
    {
        int a = 10;
        int b = 0;

        try
        {
            int c = a/b; // exception
            System.out.println("Result = " + c);
        }

        catch(ArithmeticException e)
        {
            System.out.println("Exception caught: Division by zero");
        }

        finally
        {
            System.out.println("Finally block always executes");
        }

        System.out.println("Program ends");
    }
}
