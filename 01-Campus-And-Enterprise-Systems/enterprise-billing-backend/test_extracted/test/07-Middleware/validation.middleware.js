// ======================================================
//
// Validation Middleware
//
// ======================================================

const validate = (req, res, next) => {

    const {

        name,

        email

    } = req.body;

    if (!name || !email) {

        return res.status(400).json({

            success: false,

            message: "All Fields Required"

        });

    }

    next();

};

export default validate;