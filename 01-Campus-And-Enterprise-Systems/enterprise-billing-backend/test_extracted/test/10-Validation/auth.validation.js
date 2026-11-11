import { body } from "express-validator";

export const loginValidation = [

    body("email")

        .isEmail()

        .withMessage(

            "Email Invalid"

        ),

    body("password")

        .notEmpty()

        .withMessage(

            "Password Required"

        )

];