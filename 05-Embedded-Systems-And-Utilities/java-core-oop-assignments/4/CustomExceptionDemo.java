// Program to demonstrate User Defined Exception

class CustomExceptionDemo
{
    public static void main(String args[])
    {
        String country = "USA";

        try
        {
            if(!country.equals("India"))
            {
                throw new NotFoundException("String is not equal to India");
            }

            System.out.println("String matched");
        }

        catch(NotFoundException e)
        {
            System.out.println("Exception: " + e.getMessage());
        }
    }
}


class NotFoundException extends Exception
{
    NotFoundException(String msg)
    {
        super(msg);
    }
}

