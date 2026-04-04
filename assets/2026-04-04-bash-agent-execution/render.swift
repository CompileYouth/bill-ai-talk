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
    let r = Renderer(width: 1200, height: 620, background: bg)
    rounded(NSRect(x: 78, y: 68, width: 1044, height: 484), radius: 28, fill: .white, stroke: dark, line: 4)
    drawText("bash", rect: NSRect(x: 120, y: 120, width: 960, height: 78), font: .systemFont(ofSize: 92, weight: .heavy), color: dark, align: .center, lineHeight: 96)
    drawText("让 Agent", rect: NSRect(x: 180, y: 232, width: 840, height: 58), font: .systemFont(ofSize: 58, weight: .bold), color: dark, align: .center, lineHeight: 60)
    drawText("从说到做", rect: NSRect(x: 140, y: 322, width: 920, height: 84), font: .systemFont(ofSize: 88, weight: .heavy), color: dark, align: .center, lineHeight: 90)
    watermark("@Bill的精神时光屋", rect: NSRect(x: 810, y: 492, width: 240, height: 24), color: muted)
    r.finish()
    try save(r.image, "1")

    let r2 = Renderer(width: 1200, height: 620, background: bg)
    rounded(NSRect(x: 78, y: 68, width: 1044, height: 484), radius: 28, fill: .white, stroke: dark, line: 4)
    drawText("聊天框让 AI", rect: NSRect(x: 170, y: 148, width: 860, height: 54), font: .systemFont(ofSize: 54, weight: .bold), color: dark, align: .center, lineHeight: 58)
    drawText("变得可用", rect: NSRect(x: 180, y: 228, width: 840, height: 72), font: .systemFont(ofSize: 76, weight: .heavy), color: dark, align: .center, lineHeight: 80)
    drawText("bash 让 Agent", rect: NSRect(x: 180, y: 334, width: 840, height: 52), font: .systemFont(ofSize: 52, weight: .bold), color: dark, align: .center, lineHeight: 56)
    drawText("开始干活", rect: NSRect(x: 190, y: 412, width: 820, height: 76), font: .systemFont(ofSize: 78, weight: .heavy), color: dark, align: .center, lineHeight: 82)
    watermark("@Bill的精神时光屋", rect: NSRect(x: 810, y: 492, width: 240, height: 24), color: muted)
    r2.finish()
    try save(r2.image, "2")
} catch {
    fputs("Render failed: \(error)\n", stderr)
    exit(1)
}
