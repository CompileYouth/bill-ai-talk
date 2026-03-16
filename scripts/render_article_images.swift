import AppKit
import Foundation

final class FlippedView: NSView {
    override var isFlipped: Bool { true }
}

struct Renderer {
    let width: CGFloat
    let height: CGFloat
    let image: NSImage
    let view: FlippedView

    init(width: CGFloat, height: CGFloat, background: NSColor) {
        self.width = width
        self.height = height
        self.image = NSImage(size: NSSize(width: width, height: height))
        self.view = FlippedView(frame: NSRect(x: 0, y: 0, width: width, height: height))
        image.lockFocusFlipped(true)
        background.setFill()
        NSBezierPath(rect: view.bounds).fill()
    }

    func finish() {
        image.unlockFocus()
    }
}

func makeStyle(_ alignment: NSTextAlignment = .left, lineHeight: CGFloat? = nil) -> NSMutableParagraphStyle {
    let style = NSMutableParagraphStyle()
    style.alignment = alignment
    if let lineHeight {
        style.minimumLineHeight = lineHeight
        style.maximumLineHeight = lineHeight
    }
    return style
}

func drawText(_ text: String, in rect: NSRect, font: NSFont, color: NSColor, alignment: NSTextAlignment = .left, lineHeight: CGFloat? = nil) {
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: color,
        .paragraphStyle: makeStyle(alignment, lineHeight: lineHeight)
    ]
    let attributed = NSAttributedString(string: text, attributes: attrs)
    attributed.draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading])
}

func roundedRect(_ rect: NSRect, radius: CGFloat, fill: NSColor, stroke: NSColor? = nil, lineWidth: CGFloat = 0) {
    let path = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius)
    fill.setFill()
    path.fill()
    if let stroke {
        stroke.setStroke()
        path.lineWidth = lineWidth
        path.stroke()
    }
}

func line(from: CGPoint, to: CGPoint, color: NSColor, width: CGFloat) {
    let path = NSBezierPath()
    path.move(to: from)
    path.line(to: to)
    path.lineWidth = width
    color.setStroke()
    path.stroke()
}

func arrow(from: CGPoint, to: CGPoint, color: NSColor, width: CGFloat) {
    line(from: from, to: to, color: color, width: width)
    let angle = atan2(to.y - from.y, to.x - from.x)
    let headLength: CGFloat = 18
    let headAngle: CGFloat = .pi / 6
    let p1 = CGPoint(x: to.x - headLength * cos(angle - headAngle), y: to.y - headLength * sin(angle - headAngle))
    let p2 = CGPoint(x: to.x - headLength * cos(angle + headAngle), y: to.y - headLength * sin(angle + headAngle))
    line(from: to, to: p1, color: color, width: width)
    line(from: to, to: p2, color: color, width: width)
}

func circle(center: CGPoint, radius: CGFloat, fill: NSColor, stroke: NSColor, lineWidth: CGFloat) {
    let rect = NSRect(x: center.x - radius, y: center.y - radius, width: radius * 2, height: radius * 2)
    let path = NSBezierPath(ovalIn: rect)
    fill.setFill()
    path.fill()
    stroke.setStroke()
    path.lineWidth = lineWidth
    path.stroke()
}

func jpegData(from image: NSImage) -> Data? {
    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff) else { return nil }
    return rep.representation(using: .jpeg, properties: [.compressionFactor: 0.92])
}

func save(_ image: NSImage, baseURL: URL) throws {
    guard let jpg = jpegData(from: image) else {
        throw NSError(domain: "render", code: 1)
    }
    try jpg.write(to: baseURL.appendingPathExtension("jpg"))
}

func addWatermark(_ text: String, rect: NSRect, color: NSColor) {
    drawText(
        text,
        in: rect,
        font: .systemFont(ofSize: 20, weight: .medium),
        color: color,
        alignment: .right,
        lineHeight: 22
    )
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("Usage: render_article_images.swift <assets-dir>\n", stderr)
    exit(1)
}

let outDir = URL(fileURLWithPath: args[1], isDirectory: true)
let bg1 = NSColor(calibratedRed: 0.965, green: 0.953, blue: 0.918, alpha: 1)
let bg2 = NSColor(calibratedRed: 0.972, green: 0.972, blue: 0.948, alpha: 1)
let bg3 = NSColor(calibratedRed: 0.961, green: 0.949, blue: 0.918, alpha: 1)
let card = NSColor(calibratedRed: 0.996, green: 0.989, blue: 0.965, alpha: 1)
let dark = NSColor(calibratedRed: 0.12, green: 0.12, blue: 0.12, alpha: 1)
let muted = NSColor(calibratedRed: 0.40, green: 0.40, blue: 0.40, alpha: 1)

do {
    // WeChat cover
    do {
        let r = Renderer(width: 2350, height: 1000, background: bg1)
        roundedRect(NSRect(x: 70, y: 70, width: 2210, height: 860), radius: 36, fill: card, stroke: dark, lineWidth: 5)
        line(from: CGPoint(x: 1175, y: 220), to: CGPoint(x: 1175, y: 780), color: dark, width: 5)
        drawText("真正重要的事，只剩两种", in: NSRect(x: 260, y: 150, width: 1830, height: 90), font: .systemFont(ofSize: 86, weight: .bold), color: dark, alignment: .center, lineHeight: 96)
        drawText("By Agent", in: NSRect(x: 210, y: 390, width: 760, height: 110), font: .systemFont(ofSize: 140, weight: .heavy), color: dark, alignment: .center, lineHeight: 146)
        drawText("借助 Agent 做事", in: NSRect(x: 290, y: 590, width: 600, height: 52), font: .systemFont(ofSize: 48, weight: .medium), color: muted, alignment: .center, lineHeight: 54)
        drawText("For Agent", in: NSRect(x: 1380, y: 390, width: 760, height: 110), font: .systemFont(ofSize: 140, weight: .heavy), color: dark, alignment: .center, lineHeight: 146)
        drawText("为 Agent 提供能力", in: NSRect(x: 1460, y: 590, width: 600, height: 52), font: .systemFont(ofSize: 48, weight: .medium), color: muted, alignment: .center, lineHeight: 54)
        addWatermark("@FEPulse", rect: NSRect(x: 1970, y: 845, width: 220, height: 34), color: muted)
        r.finish()
        try save(r.image, baseURL: outDir.appendingPathComponent("wechat-cover"))
    }

    // Cover
    do {
        let r = Renderer(width: 1200, height: 675, background: bg1)
        roundedRect(NSRect(x: 48, y: 48, width: 1104, height: 579), radius: 30, fill: card, stroke: dark, lineWidth: 4)
        drawText("真正重要的事，只剩两种", in: NSRect(x: 120, y: 88, width: 960, height: 70), font: .systemFont(ofSize: 46, weight: .bold), color: dark, alignment: .center, lineHeight: 54)
        line(from: CGPoint(x: 600, y: 190), to: CGPoint(x: 600, y: 500), color: dark, width: 4)
        drawText("By Agent", in: NSRect(x: 150, y: 285, width: 340, height: 80), font: .systemFont(ofSize: 72, weight: .heavy), color: dark, alignment: .center, lineHeight: 78)
        drawText("借助 Agent 做事", in: NSRect(x: 180, y: 430, width: 280, height: 40), font: .systemFont(ofSize: 28, weight: .medium), color: muted, alignment: .center, lineHeight: 32)
        drawText("For Agent", in: NSRect(x: 710, y: 285, width: 340, height: 80), font: .systemFont(ofSize: 72, weight: .heavy), color: dark, alignment: .center, lineHeight: 78)
        drawText("为 Agent 提供能力", in: NSRect(x: 740, y: 430, width: 280, height: 40), font: .systemFont(ofSize: 28, weight: .medium), color: muted, alignment: .center, lineHeight: 32)
        addWatermark("@FEPulse", rect: NSRect(x: 930, y: 575, width: 170, height: 28), color: muted)
        r.finish()
        try save(r.image, baseURL: outDir.appendingPathComponent("cover"))
    }

    // By-agent body image
    do {
        let r = Renderer(width: 1200, height: 560, background: bg2)
        drawText("By Agent 的核心，不是全自动，而是工作方式被重写", in: NSRect(x: 80, y: 52, width: 1040, height: 56), font: .systemFont(ofSize: 42, weight: .bold), color: dark, alignment: .left, lineHeight: 48)

        let left = NSRect(x: 90, y: 185, width: 250, height: 150)
        let mid = NSRect(x: 475, y: 185, width: 250, height: 150)
        let right = NSRect(x: 860, y: 185, width: 250, height: 150)
        for rect in [left, mid, right] {
            roundedRect(rect, radius: 24, fill: .white, stroke: dark, lineWidth: 4)
        }
        arrow(from: CGPoint(x: left.maxX + 5, y: 260), to: CGPoint(x: mid.minX - 20, y: 260), color: dark, width: 4)
        arrow(from: CGPoint(x: mid.maxX + 5, y: 260), to: CGPoint(x: right.minX - 20, y: 260), color: dark, width: 4)

        drawText("人定义\n目标和边界", in: NSRect(x: 110, y: 206, width: 210, height: 52), font: .systemFont(ofSize: 20, weight: .medium), color: muted, alignment: .center, lineHeight: 24)
        drawText("提问题", in: NSRect(x: 110, y: 270, width: 210, height: 42), font: .systemFont(ofSize: 34, weight: .bold), color: dark, alignment: .center, lineHeight: 38)

        drawText("整理、生成\n分析、推进", in: NSRect(x: 495, y: 206, width: 210, height: 52), font: .systemFont(ofSize: 20, weight: .medium), color: muted, alignment: .center, lineHeight: 24)
        drawText("Agent 执行", in: NSRect(x: 495, y: 270, width: 210, height: 42), font: .systemFont(ofSize: 34, weight: .bold), color: dark, alignment: .center, lineHeight: 38)

        drawText("筛选、取舍\n负责结果", in: NSRect(x: 880, y: 206, width: 210, height: 52), font: .systemFont(ofSize: 20, weight: .medium), color: muted, alignment: .center, lineHeight: 24)
        drawText("人做判断", in: NSRect(x: 880, y: 270, width: 210, height: 42), font: .systemFont(ofSize: 34, weight: .bold), color: dark, alignment: .center, lineHeight: 38)

        drawText("重点不是 Agent 干了多少，而是你有没有真的把它用进核心流程。", in: NSRect(x: 110, y: 430, width: 980, height: 48), font: .systemFont(ofSize: 28, weight: .semibold), color: dark, alignment: .center, lineHeight: 34)
        addWatermark("@FEPulse", rect: NSRect(x: 960, y: 490, width: 180, height: 28), color: muted)
        r.finish()
        try save(r.image, baseURL: outDir.appendingPathComponent("by"))
    }

    // For-agent body image
    do {
        let r = Renderer(width: 1200, height: 620, background: bg3)
        drawText("For Agent，就是给 Agent 修路", in: NSRect(x: 90, y: 48, width: 1020, height: 56), font: .systemFont(ofSize: 42, weight: .bold), color: dark, alignment: .left, lineHeight: 48)

        circle(center: CGPoint(x: 600, y: 310), radius: 110, fill: .white, stroke: dark, lineWidth: 4)
        drawText("Agent", in: NSRect(x: 490, y: 285, width: 220, height: 48), font: .systemFont(ofSize: 40, weight: .heavy), color: dark, alignment: .center, lineHeight: 44)
        drawText("能力落地中心", in: NSRect(x: 490, y: 336, width: 220, height: 32), font: .systemFont(ofSize: 22, weight: .medium), color: muted, alignment: .center, lineHeight: 28)

        let tool = NSRect(x: 510, y: 126, width: 180, height: 60)
        let data = NSRect(x: 150, y: 230, width: 180, height: 60)
        let api = NSRect(x: 870, y: 230, width: 180, height: 60)
        let kb = NSRect(x: 140, y: 430, width: 210, height: 60)
        let flow = NSRect(x: 850, y: 430, width: 210, height: 60)
        let nodes: [(String, NSRect)] = [
            ("工具", tool),
            ("数据", data),
            ("接口", api),
            ("知识库", kb),
            ("工作流", flow)
        ]
        for (label, rect) in nodes {
            roundedRect(rect, radius: 16, fill: .white, stroke: dark, lineWidth: 3)
            drawText(label, in: NSRect(x: rect.minX, y: rect.minY + 12, width: rect.width, height: 32), font: .systemFont(ofSize: 28, weight: .bold), color: dark, alignment: .center, lineHeight: 32)
        }
        line(from: CGPoint(x: 600, y: 200), to: CGPoint(x: 600, y: tool.maxY), color: dark, width: 4)
        line(from: CGPoint(x: 490, y: 270), to: CGPoint(x: data.maxX, y: data.midY), color: dark, width: 4)
        line(from: CGPoint(x: 710, y: 270), to: CGPoint(x: api.minX, y: api.midY), color: dark, width: 4)
        line(from: CGPoint(x: 500, y: 380), to: CGPoint(x: kb.maxX, y: kb.midY), color: dark, width: 4)
        line(from: CGPoint(x: 700, y: 380), to: CGPoint(x: flow.minX, y: flow.midY), color: dark, width: 4)

        drawText("谁在提供这些东西，谁就在参与 Agent 时代的价值分配。", in: NSRect(x: 110, y: 536, width: 980, height: 42), font: .systemFont(ofSize: 28, weight: .semibold), color: dark, alignment: .center, lineHeight: 34)
        addWatermark("@FEPulse", rect: NSRect(x: 960, y: 550, width: 180, height: 28), color: muted)
        r.finish()
        try save(r.image, baseURL: outDir.appendingPathComponent("for"))
    }
} catch {
    fputs("Render failed: \(error)\n", stderr)
    exit(1)
}
