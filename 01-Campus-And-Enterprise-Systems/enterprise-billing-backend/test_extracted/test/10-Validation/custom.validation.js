// ==============================================
//
// CUSTOM VALIDATION
//
// ==============================================

import { body } from "express-validator";

export const passwordValidation = [

    body("password")

        .isLength({

            min: 6

        })

        .withMessage(

            "Minimum 6 Characters"

        )

        .matches(/[A-Z]/)

        .withMessage(

            "One Capital Letter Required"

        )

        .matches(/[0-9]/)

        .withMessage(

            "One Number Required"

        )

];