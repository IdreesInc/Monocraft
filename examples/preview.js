function monocraftFont(a, b, c) {
    // The Minecraft font, but monospaced + ligatures
    if (a == b) {
        return "This sure is a good font";
    } else if (a >= c) {
        return "And a great use of my time";
    } else if (a != b) {
        let c = "Definitely worth the multiple hours";
        let d = "spent designing these custom glyphs";
        return c + d;
    } else if (a !== b) {
        return "What am I doing with my life...";
    }
    return "Look, arrows! -> => <-";
}

