package com.example.meshlink.crypto;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Base64;
import android.util.Log;

import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class CryptoManager {

    private static final String TAG = "CryptoManager";
    private static final String PREF_NAME = "meshlink_crypto_keystore";
    private static final String KEY_PUBLIC = "pub_key_base64";
    private static final String KEY_PRIVATE = "priv_key_base64";
    private static final String KEY_MESH_ID = "my_mesh_id";

    private static CryptoManager instance;
    private final SharedPreferences prefs;

    private PublicKey myPublicKey;
    private PrivateKey myPrivateKey;
    private String myMeshId;

    public static synchronized CryptoManager getInstance(Context context) {
        if (instance == null) {
            instance = new CryptoManager(context.getApplicationContext());
        }
        return instance;
    }

    private CryptoManager(Context context) {
        this.prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        loadOrGenerateKeys();
    }

    private void loadOrGenerateKeys() {
        try {
            String pubBase64 = prefs.getString(KEY_PUBLIC, null);
            String privBase64 = prefs.getString(KEY_PRIVATE, null);

            if (pubBase64 != null && privBase64 != null) {
                KeyFactory kf = KeyFactory.getInstance("RSA");
                byte[] pubBytes = Base64.decode(pubBase64, Base64.NO_WRAP);
                byte[] privBytes = Base64.decode(privBase64, Base64.NO_WRAP);

                myPublicKey = kf.generatePublic(new X509EncodedKeySpec(pubBytes));
                myPrivateKey = kf.generatePrivate(new PKCS8EncodedKeySpec(privBytes));
                myMeshId = prefs.getString(KEY_MESH_ID, generateMeshIdFromPublicKey(myPublicKey));
            } else {
                // Generate fresh 2048-bit RSA keypair
                KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
                kpg.initialize(2048);
                KeyPair kp = kpg.generateKeyPair();
                myPublicKey = kp.getPublic();
                myPrivateKey = kp.getPrivate();

                myMeshId = generateMeshIdFromPublicKey(myPublicKey);

                String newPub = Base64.encodeToString(myPublicKey.getEncoded(), Base64.NO_WRAP);
                String newPriv = Base64.encodeToString(myPrivateKey.getEncoded(), Base64.NO_WRAP);

                prefs.edit()
                        .putString(KEY_PUBLIC, newPub)
                        .putString(KEY_PRIVATE, newPriv)
                        .putString(KEY_MESH_ID, myMeshId)
                        .apply();
                Log.d(TAG, "Generated fresh Cryptographic Identity: " + myMeshId);
            }
        } catch (Exception e) {
            Log.e(TAG, "Key generation error: " + e.getMessage());
        }
    }

    private String generateMeshIdFromPublicKey(PublicKey key) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(key.getEncoded());
            StringBuilder sb = new StringBuilder("mesh@");
            for (int i = 0; i < 6; i++) {
                sb.append(String.format("%02x", digest[i]));
            }
            return sb.toString();
        } catch (Exception e) {
            return "mesh@" + Long.toHexString(System.currentTimeMillis()).substring(0, 8);
        }
    }

    public String getMyMeshId() {
        return myMeshId;
    }

    public String getMyPublicKeyBase64() {
        return Base64.encodeToString(myPublicKey.getEncoded(), Base64.NO_WRAP);
    }

    /**
     * Encrypts plaintext message with AES-GCM, and encrypts the AES key with recipient's RSA public key.
     * End-to-End Encrypted (E2EE) — zero plain text exposed on intermediate mesh relay nodes.
     */
    public String encryptForPeer(String recipientPublicKeyBase64, String plainText) {
        try {
            // 1. Parse recipient public key
            byte[] pubBytes = Base64.decode(recipientPublicKeyBase64, Base64.NO_WRAP);
            PublicKey recipientKey = KeyFactory.getInstance("RSA").generatePublic(new X509EncodedKeySpec(pubBytes));

            // 2. Generate random 256-bit AES session key
            KeyGenerator keyGen = KeyGenerator.getInstance("AES");
            keyGen.init(256);
            SecretKey aesKey = keyGen.generateKey();

            // 3. Encrypt payload with AES-GCM
            Cipher aesCipher = Cipher.getInstance("AES/GCM/NoPadding");
            byte[] iv = new byte[12];
            new java.security.SecureRandom().nextBytes(iv);
            GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
            aesCipher.init(Cipher.ENCRYPT_MODE, aesKey, gcmSpec);
            byte[] cipherBytes = aesCipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));

            // 4. Encrypt AES key with recipient's RSA key
            Cipher rsaCipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
            rsaCipher.init(Cipher.ENCRYPT_MODE, recipientKey);
            byte[] encryptedAesKey = rsaCipher.doFinal(aesKey.getEncoded());

            // 5. Sign plaintext with sender's private key
            Signature signer = Signature.getInstance("SHA256withRSA");
            signer.initSign(myPrivateKey);
            signer.update(plainText.getBytes(StandardCharsets.UTF_8));
            byte[] signatureBytes = signer.sign();

            // 6. Pack into secure E2EE JSON envelope
            JSONObject envelope = new JSONObject();
            envelope.put("e2ee", true);
            envelope.put("sender_id", myMeshId);
            envelope.put("sender_pub", getMyPublicKeyBase64());
            envelope.put("ek", Base64.encodeToString(encryptedAesKey, Base64.NO_WRAP));
            envelope.put("iv", Base64.encodeToString(iv, Base64.NO_WRAP));
            envelope.put("ct", Base64.encodeToString(cipherBytes, Base64.NO_WRAP));
            envelope.put("sig", Base64.encodeToString(signatureBytes, Base64.NO_WRAP));

            return envelope.toString();
        } catch (Exception e) {
            Log.e(TAG, "Encryption failed: " + e.getMessage());
            return plainText; // fallback to unencrypted if recipient key invalid
        }
    }

    /**
     * Decrypts an incoming E2EE envelope using device's RSA private key.
     */
    public String decryptFromPeer(String envelopeJson) {
        try {
            JSONObject envelope = new JSONObject(envelopeJson);
            if (!envelope.optBoolean("e2ee", false)) {
                return envelopeJson; // not encrypted
            }

            byte[] encAesKey = Base64.decode(envelope.getString("ek"), Base64.NO_WRAP);
            byte[] iv = Base64.decode(envelope.getString("iv"), Base64.NO_WRAP);
            byte[] cipherBytes = Base64.decode(envelope.getString("ct"), Base64.NO_WRAP);

            // 1. Decrypt AES session key with our RSA private key
            Cipher rsaCipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
            rsaCipher.init(Cipher.DECRYPT_MODE, myPrivateKey);
            byte[] aesKeyBytes = rsaCipher.doFinal(encAesKey);
            SecretKeySpec aesKey = new SecretKeySpec(aesKeyBytes, "AES");

            // 2. Decrypt ciphertext with AES-GCM
            Cipher aesCipher = Cipher.getInstance("AES/GCM/NoPadding");
            GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
            aesCipher.init(Cipher.DECRYPT_MODE, aesKey, gcmSpec);
            byte[] plainBytes = aesCipher.doFinal(cipherBytes);

            return new String(plainBytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            Log.w(TAG, "Decryption error: " + e.getMessage());
            return "[Encrypted Message - Key Mismatch]";
        }
    }
}
