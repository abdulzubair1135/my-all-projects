// ============================================================
//
// FILE : async-handler.js
//
// PURPOSE
// --------
//
// try-catch baar baar likhne ki zarurat kam karna.
//
// ============================================================

const asyncHandler = (fn) => {

    return (req, res, next) => {

        Promise.resolve(

            fn(req, res, next)

        ).catch(next);

    };

};

export default asyncHandler;