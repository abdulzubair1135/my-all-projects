// ============================================================
//
// RESPONSE HELPER
//
// ============================================================

export const success = (

    res,

    message,

    data = null,

    status = 200

) => {

    return res.status(status).json({

        success: true,

        message,

        data

    });

};

export const error = (

    res,

    message,

    status = 500

) => {

    return res.status(status).json({

        success: false,

        message

    });

};