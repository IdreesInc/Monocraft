function exampleCode(a, b, c) {
    if (a == b && a !== b) {
        console.log("Monocraft is great!");
        return a;
    } else if (a > b || b <= c) {
        // Hey look, -> arrow <- ligatures!
        return b;
    } else {
        for (let i = 0; i < 10; i++) {
            c += i;
        }
        let list = [1, 2, 3];
        return list.map(value => value + c);
    }
}