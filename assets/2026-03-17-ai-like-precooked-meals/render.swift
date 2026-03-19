import AppKit
import Foundation

final class FlippedView: NSView {
    override var isFlipped: Bool { true }
}

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

func line(_ from: CGPoint, _ to: CGPoint, _ color: NSColor, _ width: CGFloat) {
    let path = NSBezierPath()
    path.move(to: from)
    path.line(to: to)
    path.lineWidth = width
    color.setStroke()
    path.stroke()
}

func arrow(_ from: CGPoint, _ to: CGPoint, _ color: NSColor, _ width: CGFloat) {
    line(from, to, color, width)
    let angle = atan2(to.y - from.y, to.x - from.x)
    let len: CGFloat = 18
    let delta: CGFloat = .pi / 6
    let p1 = CGPoint(x: to.x - len * cos(angle - delta), y: to.y - len * sin(angle - delta))
    let p2 = CGPoint(x: to.x - len * cos(angle + delta), y: to.y - len * sin(angle + delta))
    line(to, p1, color, width)
    line(to, p2, color, width)
}

func jpegData(_ image: NSImage) -> Data? {
    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff) else { return nil }
    return rep.representation(using: .jpeg, properties: [.compressionFactor: 0.9])
}

func watermark(_ text: String, rect: NSRect, color: NSColor) {
    drawText(text, rect: rect, font: .systemFont(ofSize: 18, weight: .medium), color: color, align: .right, lineHeight: 20)
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("Usage: render_precooked_ai_images.swift <assets-dir>\n", stderr)
    exit(1)
}

let outDir = URL(fileURLWithPath: args[1], isDirectory: true)
let bg = NSColor(calibratedRed: 0.966, green: 0.953, blue: 0.921, alpha: 1)
let bg2 = NSColor(calibratedRed: 0.973, green: 0.971, blue: 0.947, alpha: 1)
let card = NSColor(calibratedRed: 0.997, green: 0.992, blue: 0.972, alpha: 1)
let dark = NSColor(calibratedRed: 0.12, green: 0.12, blue: 0.12, alpha: 1)
let muted = NSColor(calibratedRed: 0.42, green: 0.42, blue: 0.42, alpha: 1)

func save(_ image: NSImage, _ name: String) throws {
    guard let jpg = jpegData(image) else { throw NSError(domain: "render", code: 1) }
    try jpg.write(to: outDir.appendingPathComponent(name).appendingPathExtension("jpg"))
}

do {
    // body image 1
    do {
        let r = Renderer(width: 1200, height: 620, background: bg2)
        rounded(NSRect(x: 80, y: 70, width: 1040, height: 480), radius: 30, fill: .white, stroke: dark, line: 4)
        drawText("预制菜真正改变的，", rect: NSRect(x: 150, y: 150, width: 900, height: 72), font: .systemFont(ofSize: 56, weight: .bold), color: dark, align: .center, lineHeight: 62)
        drawText("不是一道菜，", rect: NSRect(x: 150, y: 245, width: 900, height: 86), font: .systemFont(ofSize: 82, weight: .heavy), color: dark, align: .center, lineHeight: 88)
        drawText("而是整个经营方式。", rect: NSRect(x: 150, y: 345, width: 900, height: 86), font: .systemFont(ofSize: 82, weight: .heavy), color: dark, align: .center, lineHeight: 88)
        watermark("@Bill的精神时光屋", rect: NSRect(x: 700, y: 470, width: 320, height: 28), color: muted)
        r.finish()
        try save(r.image, "1")
    }

    // body image 2
    do {
        let r = Renderer(width: 1200, height: 620, background: bg)
        rounded(NSRect(x: 80, y: 70, width: 1040, height: 480), radius: 30, fill: .white, stroke: dark, line: 4)
        drawText("今天面对 AI，", rect: NSRect(x: 150, y: 150, width: 900, height: 72), font: .systemFont(ofSize: 56, weight: .bold), color: dark, align: .center, lineHeight: 62)
        drawText("最重要的不是研究它，", rect: NSRect(x: 120, y: 245, width: 960, height: 86), font: .systemFont(ofSize: 56, weight: .bold), color: dark, align: .center, lineHeight: 62)
        drawText("而是先把它用起来。", rect: NSRect(x: 120, y: 345, width: 960, height: 86), font: .systemFont(ofSize: 82, weight: .heavy), color: dark, align: .center, lineHeight: 88)
        watermark("@Bill的精神时光屋", rect: NSRect(x: 700, y: 470, width: 320, height: 28), color: muted)
        r.finish()
        try save(r.image, "2")
    }
} catch {
    fputs("Render failed: \(error)\n", stderr)
    exit(1)
}
