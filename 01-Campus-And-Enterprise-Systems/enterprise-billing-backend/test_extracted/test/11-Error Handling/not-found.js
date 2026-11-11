// ============================================================
//
// 404 Middleware
//
// ============================================================

const notFound = (req, res) => {

    res.status(404).json({

        success: false,

        message: "API Not Found"

    });

};

export default notFound;