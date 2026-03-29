import AppKit
import Foundation

struct Renderer {
    let image: NSImage

    init(width: CGFloat, height: CGFloat, background: NSColor) {
        self.image = NSImage(size: NSSize(width: width, height: height))
        image.lockFocusFlipped(true)
        background.setFill()
        NSBezierPath(rect: NSRect(x: 0, y: 0, width: width, height: height)).fill()
    }

    func finish() {
        image.unlockFocus()
    }
}

func style(_ alignment: NSTextAlignment = .left, _ lineHeight: CGFloat? = nil) -> NSMutableParagraphStyle {
    let s = NSMutableParagraphStyle()
    s.alignment = alignment
    if let lineHeight {
        s.minimumLineHeight = lineHeight
        s.maximumLineHeight = lineHeight
    }
    return s
}

func drawText(_ text: String, rect: NSRect, font: NSFont, color: NSColor, align: NSTextAlignment = .left, lineHeight: CGFloat? = nil) {
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: color,
        .paragraphStyle: style(align, lineHeight)
    ]
    NSAttributedString(string: text, attributes: attrs).draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading])
}

func rounded(_ rect: NSRect, radius: CGFloat, fill: NSColor, stroke: NSColor, line: CGFloat) {
    let path = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius)
    fill.setFill()
    path.fill()
    stroke.setStroke()
    path.lineWidth = line
    path.stroke()
}

func watermark(_ text: String, rect: NSRect, color: NSColor) {
    drawText(text, rect: rect, font: .systemFont(ofSize: 18, weight: .medium), color: color, align: .right, lineHeight: 22)
}

func jpegData(_ image: NSImage) -> Data? {
    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff) else { return nil }
    return rep.representation(using: .jpeg, properties: [.compressionFactor: 0.9])
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("Usage: render.swift <assets-dir>\n", stderr)
    exit(1)
}

let outDir = URL(fileURLWithPath: args[1], isDirectory: true)
let bg = NSColor(calibratedRed: 0.969, green: 0.956, blue: 0.926, alpha: 1)
let dark = NSColor(calibratedRed: 0.11, green: 0.11, blue: 0.11, alpha: 1)
let muted = NSColor(calibratedRed: 0.40, green: 0.40, blue: 0.40, alpha: 1)

func save(_ image: NSImage, _ name: String) throws {
    guard let jpg = jpegData(image) else { throw NSError(domain: "render", code: 1) }
    try jpg.write(to: outDir.appendingPathComponent(name).appendingPathExtension("jpg"))
}

do {
    do {
        let r = Renderer(width: 1200, height: 620, background: bg)
        rounded(NSRect(x: 78, y: 68, width: 1044, height: 484), radius: 28, fill: .white, stroke: dark, line: 4)
        drawText("顶级模型和普通模型", rect: NSRect(x: 130, y: 150, width: 940, height: 58), font: .systemFont(ofSize: 54, weight: .bold), color: dark, align: .center, lineHeight: 58)
        drawText("真正拉开差距的", rect: NSRect(x: 180, y: 228, width: 840, height: 64), font: .systemFont(ofSize: 60, weight: .bold), color: dark, align: .center, lineHeight: 66)
        drawText("是能力层次", rect: NSRect(x: 140, y: 318, width: 920, height: 84), font: .systemFont(ofSize: 84, weight: .heavy), color: dark, align: .center, lineHeight: 88)
        watermark("@Bill的精神时光屋", rect: NSRect(x: 820, y: 492, width: 230, height: 24), color: muted)
        r.finish()
        try save(r.image, "1")
    }

    do {
        let r = Renderer(width: 1200, height: 620, background: bg)
        rounded(NSRect(x: 78, y: 68, width: 1044, height: 484), radius: 28, fill: .white, stroke: dark, line: 4)
        drawText("第一层差得不明显", rect: NSRect(x: 160, y: 150, width: 880, height: 58), font: .systemFont(ofSize: 54, weight: .bold), color: dark, align: .center, lineHeight: 58)
        drawText("越往后", rect: NSRect(x: 260, y: 232, width: 680, height: 66), font: .systemFont(ofSize: 66, weight: .bold), color: dark, align: .center, lineHeight: 70)
        drawText("差距越大", rect: NSRect(x: 150, y: 322, width: 900, height: 84), font: .systemFont(ofSize: 84, weight: .heavy), color: dark, align: .center, lineHeight: 88)
        watermark("@Bill的精神时光屋", rect: NSRect(x: 820, y: 492, width: 230, height: 24), color: muted)
        r.finish()
        try save(r.image, "2")
    }
} catch {
    fputs("Render failed: \\(error)\\n", stderr)
    exit(1)
}
