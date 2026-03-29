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
        drawText("顶级 AI 产品", rect: NSRect(x: 200, y: 148, width: 800, height: 56), font: .systemFont(ofSize: 58, weight: .bold), color: dark, align: .center, lineHeight: 60)
        drawText("不该只问", rect: NSRect(x: 220, y: 224, width: 760, height: 64), font: .systemFont(ofSize: 64, weight: .bold), color: dark, align: .center, lineHeight: 68)
        drawText("谁最强", rect: NSRect(x: 140, y: 302, width: 920, height: 86), font: .systemFont(ofSize: 90, weight: .heavy), color: dark, align: .center, lineHeight: 92)
        drawText("更该问谁适合什么场景", rect: NSRect(x: 100, y: 404, width: 1000, height: 52), font: .systemFont(ofSize: 42, weight: .bold), color: dark, align: .center, lineHeight: 48)
        watermark("@Bill的精神时光屋", rect: NSRect(x: 820, y: 492, width: 230, height: 24), color: muted)
        r.finish()
        try save(r.image, "1")
    }

    do {
        let r = Renderer(width: 1200, height: 620, background: bg)
        rounded(NSRect(x: 78, y: 68, width: 1044, height: 484), radius: 28, fill: .white, stroke: dark, line: 4)
        drawText("ChatGPT 负责日常", rect: NSRect(x: 140, y: 176, width: 920, height: 54), font: .systemFont(ofSize: 50, weight: .bold), color: dark, align: .center, lineHeight: 56)
        drawText("Claude Code 负责复杂代码", rect: NSRect(x: 90, y: 270, width: 1020, height: 56), font: .systemFont(ofSize: 46, weight: .bold), color: dark, align: .center, lineHeight: 56)
        drawText("Gemini 负责作图和多模态", rect: NSRect(x: 100, y: 364, width: 1000, height: 56), font: .systemFont(ofSize: 46, weight: .bold), color: dark, align: .center, lineHeight: 56)
        watermark("@Bill的精神时光屋", rect: NSRect(x: 820, y: 492, width: 230, height: 24), color: muted)
        r.finish()
        try save(r.image, "2")
    }
} catch {
    fputs("Render failed: \(error)\n", stderr)
    exit(1)
}
