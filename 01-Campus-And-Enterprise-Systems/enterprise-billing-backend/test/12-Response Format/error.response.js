// ============================================================
//
// ERROR RESPONSE
//
// ============================================================

const errorResponse = (

    res,

    message,

    statusCode = 500

) => {

    return res.status(statusCode).json({

        success: false,

        message

    });

};

export default errorResponse;