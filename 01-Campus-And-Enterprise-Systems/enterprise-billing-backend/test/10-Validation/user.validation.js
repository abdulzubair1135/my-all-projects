// ============================================================
//
// USER VALIDATION
//
// ============================================================

import { body } from "express-validator";

export const createUserValidation = [

    body("name")

        .notEmpty()

        .withMessage("Name is Required")

        .isLength({

            min: 3

        })

        .withMessage(

            "Minimum 3 Characters"

        ),

    body("email")

        .isEmail()

        .withMessage(

            "Invalid Email"

        ),

    body("phone")

        .isMobilePhone()

        .withMessage(

            "Invalid Phone Number"

        )

];