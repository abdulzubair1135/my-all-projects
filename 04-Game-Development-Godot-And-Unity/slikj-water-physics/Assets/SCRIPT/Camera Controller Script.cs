using UnityEngine;

public class FirstPersonCamera : MonoBehaviour
{
    public Transform player;
    public float sensitivity = 10f;

    private float xRotation = 0f;

    void Start()
    {
        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        float mouseX = Input.GetAxis("Mouse X") * sensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * sensitivity;

        Debug.Log("MouseX: " + mouseX);
        Debug.Log("MouseY: " + mouseY);

        xRotation -= mouseY;
        xRotation = Mathf.Clamp(xRotation, -90f, 90f);

        // Rotate the camera around its local X-axis
        transform.localRotation = Quaternion.Euler(xRotation, transform.rotation.y, 0f);

        // Rotate the player around its local Y-axis
        player.Rotate(Vector3.up * mouseX);
    }
}
