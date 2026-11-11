Array.prototype.myConcat = function (...arrays) {
    const result = [...this];
    for (const array of arrays) {
        if (Array.isArray(array)) {
            result.push(...array);
        } else {
            result.push(array);
        }
    }
    return result;
};
const arr = [1, 2, 3, 4];
const arr2 = [ 5, 6, [1]];
const arr3 = [7, 8, 9];
const concat = arr.myConcat(arr2, arr3, 10);
console.log(concat);