// Program to demonstrate Inner Class

class InnerClassDemo
{
    public static void main(String args[])
    {
        Shape s = new Shape();              // outer class object
        Shape.Pyramid p = s.new Pyramid();  // inner class object

        p.pyramids(5);                      // calling pyramid method
    }
}

class Shape
{
    // Inner class
    class Pyramid
    {
        void pyramids(int rows)
        {
            for(int i=1;i<=rows;i++)
            {
                for(int j=1;j<=i;j++)
                {
                    System.out.print("* ");
                }
                System.out.println();
            }
        }
    }
}


