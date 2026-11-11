// ============================================================
//
// PAGINATION RESPONSE
//
// ============================================================

const paginationResponse = (

    res,

    data,

    page,

    limit,

    total

) => {

    return res.status(200).json({

        success: true,

        page,

        limit,

        total,

        totalPages: Math.ceil(total / limit),

        data

    });

};

export default paginationResponse;