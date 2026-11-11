// ============================================================
//
// FILE : error.middleware.js
//
// PURPOSE
// --------
//
// Global Error Handler
//
// ============================================================

const errorHandler = (

    err,

    req,

    res,

    next

) => {

    console.error(err);

    res.status(

        err.statusCode || 500

    ).json({

        success: false,

        message:

            err.message ||

            "Internal Server Error"

    });

};

export default errorHandler;