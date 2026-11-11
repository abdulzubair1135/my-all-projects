using UnityEngine;

public class PlayerMovement : MonoBehaviour
{
    // --- Player movement related variables ---
    public float moveSpeed = 5f;   // Normal walk speed
    public float runSpeed = 8f;    // Run karne ka speed
    public float jumpForce = 8f;   // Jump ki force
    public float gravityMod = 2f;  // Gravity ko thoda strong/weak karne ke liye multiplier

    private float currentMoveSpeed;        // Abhi ka current movement speed (walk/run)
    private CharacterController characterController;  // Character Controller component reference
    private Vector3 movement;              // Movement vector (x, y, z)

    // --- Mouse look and camera related variables ---
    public Transform playerviewPoint;      // Camera ka position point (usually head ke jagah par)
    public float mouseSensitivity;         // Mouse sensitivity
    private float verticalRotation;        // Up/Down rotation value
    private Vector2 mouseInput;            // Mouse ka input (X = left/right, Y = up/down)
    public bool invertLook;                // Agar true ho toh up/down inverted hoga
    private Camera playerCamera;           // Main camera ka reference

    void Start()
    {
        // Start me character controller aur camera assign karte hai
        characterController = GetComponent<CharacterController>();
        playerCamera = Camera.main;

        // Mouse cursor ko lock karte hai taaki game ke beech me cursor screen se bahar na jaye
        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        // --- Mouse Look (Player rotation and view angle) ---

        // Mouse ka X aur Y input lena (Raw matlab smoothing nahi)
        mouseInput = new Vector2(Input.GetAxisRaw("Mouse X"), Input.GetAxisRaw("Mouse Y")) * mouseSensitivity;

        // Player ko horizontally (Y-axis) rotate karna
        transform.rotation = Quaternion.Euler(
            transform.rotation.eulerAngles.x,
            transform.rotation.eulerAngles.y + mouseInput.x,
            transform.rotation.eulerAngles.z
        );

        // Vertical rotation update karna (mouse Y se)
        verticalRotation += mouseInput.y;
        verticalRotation = Mathf.Clamp(verticalRotation, -60f, 60f); // Limit karte hai camera ko taaki 360° na ghoome

        // Agar invertLook ON hai toh opposite rotation dena
        if (invertLook)
        {
            playerviewPoint.rotation = Quaternion.Euler(
                verticalRotation,
                playerviewPoint.eulerAngles.y,
                playerviewPoint.eulerAngles.z
            );
        }
        else
        {
            playerviewPoint.rotation = Quaternion.Euler(
                -verticalRotation,
                playerviewPoint.eulerAngles.y,
                playerviewPoint.eulerAngles.z
            );
        }


        // --- Player Movement (WASD + Jump) ---

        float horizontalInput = Input.GetAxis("Horizontal");  // A / D keys
        float verticalInput = Input.GetAxis("Vertical");      // W / S keys

        // Agar Left Shift daba ho toh run speed, warna normal walk
        currentMoveSpeed = Input.GetKey(KeyCode.LeftShift) ? runSpeed : moveSpeed;

        // Movement direction banana player ke forward aur right ke hisaab se
        Vector3 moveDir = (transform.forward * verticalInput + transform.right * horizontalInput).normalized;

        // Final movement vector me speed apply karna
        movement.x = moveDir.x * currentMoveSpeed;
        movement.z = moveDir.z * currentMoveSpeed;

        // --- Ground check and Jump ---

        if (characterController.isGrounded)
        {
            // Agar player ground pe hai aur neeche ki taraf move kar raha hai toh thoda neeche hold kar lo
            if (movement.y < 0f)
                movement.y = -2f; // ye value thoda player ko ground pe chipka ke rakhti hai

            // Jump input
            if (Input.GetButtonDown("Jump"))
            {
                movement.y = jumpForce; // Jump force apply karte hai
            }
        }

        // --- Gravity Apply karna ---
        movement.y += Physics.gravity.y * gravityMod * Time.deltaTime;

        // CharacterController ke Move() function se actual movement apply hota hai
        characterController.Move(movement * Time.deltaTime);


        // --- Cursor Lock/Unlock Logic ---

        // ESC press karne pe cursor unlock kar do (so user can click UI etc.)
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            Cursor.lockState = CursorLockMode.None;
        }
        // Agar cursor unlocked hai, aur left mouse click kare toh wapas lock kar do
        else if (Cursor.lockState == CursorLockMode.None)
        {
            if (Input.GetMouseButton(0))
            {
                Cursor.lockState = CursorLockMode.Locked;
            }
        }
    }

    private void LateUpdate()
    {
        // --- Camera Position aur Rotation Update ---
        // Camera ko player ke viewpoint (usually head) ke sath sync karte hai
        playerCamera.transform.position = playerviewPoint.position;
        playerCamera.transform.rotation = playerviewPoint.rotation;
    }
}
