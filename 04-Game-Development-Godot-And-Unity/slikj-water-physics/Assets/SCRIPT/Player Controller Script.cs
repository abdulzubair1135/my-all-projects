using UnityEngine;

public class PlayerController : MonoBehaviour
{
    public float walkSpeed = 5f;
    public float runSpeed = 10f;
    private Rigidbody rb;
    private Camera mainCamera;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        mainCamera = Camera.main;
    }

    void Update()
    {
        // Check input values
        float moveHorizontal = Input.GetAxis("Horizontal");
        float moveVertical = Input.GetAxis("Vertical");

        Debug.Log("Horizontal: " + moveHorizontal);
        Debug.Log("Vertical: " + moveVertical);

        Vector3 movement = new Vector3(moveHorizontal, 0.0f, moveVertical);
        rb.linearVelocity = transform.forward * movement.magnitude * GetSpeed();

        // Camera rotation
        float mouseX = Input.GetAxis("Mouse X");
        float mouseY = Input.GetAxis("Mouse Y");

        Debug.Log("MouseX: " + mouseX);
        Debug.Log("MouseY: " + mouseY);

        Quaternion deltaRotationX = Quaternion.Euler(mainCamera.transform.localEulerAngles.x - mouseY, 0.0f, 0.0f);
        Quaternion deltaRotationY = Quaternion.Euler(0.0f, mainCamera.transform.localEulerAngles.y + mouseX, 0.0f);

        mainCamera.transform.localRotation = deltaRotationX;
        transform.rotation *= deltaRotationY;
    }

    private float GetSpeed()
    {
        if (Input.GetKey(KeyCode.LeftControl))
        {
            Debug.Log("Walking");
            return walkSpeed; // Walking speed
        }
        else if (Input.GetKey(KeyCode.LeftShift))
        {
            Debug.Log("Sprinting");
            return runSpeed; // Sprinting speed
        }
        else
        {
            Debug.Log("Running");
            return runSpeed; // Running speed
        }
    }
}
