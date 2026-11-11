// ============================================================
//
// FILE : validation.middleware.js
//
// PURPOSE
// --------
//
// express-validator Errors Handle Karna
//
// ============================================================

import { validationResult } from "express-validator";

const validate = (req, res, next) => {

    const errors = validationResult(req);

    if (!errors.isEmpty()) {

        return res.status(400).json({

            success: false,

            errors: errors.array()

        });

    }

    next();

};

export default validate;