// Program to demonstrate Abstract Class and Inheritance

class AbstractDemo
{
    public static void main(String args[])
    {
        // People p = new People();  // ERROR: Cannot create object of abstract class

        Student s = new Student();  // object of subclass
        s.display();                // calling implemented method
    }
}

abstract class People
{
    String name;

    // Abstract method
    abstract void display();
}

// Subclass Student inheriting People
class Student extends People
{
    void display()
    {
        name = "Rahul";
        System.out.println("Student Name: " + name);
    }
}


