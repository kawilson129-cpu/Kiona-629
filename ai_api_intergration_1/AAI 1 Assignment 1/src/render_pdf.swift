// Offline PDF layout QA only. These PNGs render a report, not an application.
import Foundation
import AppKit
import PDFKit

guard CommandLine.arguments.count == 3,
      let document = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))
else { fatalError("Usage: render_pdf.swift report.pdf output-directory") }
let output = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
var pages: [[String: Any]] = []
for i in 0..<document.pageCount {
    guard let page = document.page(at: i) else { fatalError("Missing PDF page") }
    let image = page.thumbnail(of: NSSize(width: 1224, height: 1584), for: .mediaBox)
    guard let tiff = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiff),
          let png = bitmap.representation(using: .png, properties: [:])
    else { fatalError("PDF rendering failed") }
    try png.write(to: output.appendingPathComponent("report-page-\(i + 1).png"))
    pages.append(["page": i + 1, "text": page.string ?? "", "width": page.bounds(for: .mediaBox).width,
                  "height": page.bounds(for: .mediaBox).height])
}
let json = try JSONSerialization.data(withJSONObject: ["scope": "Offline PDF rendering; no API execution",
    "page_count": document.pageCount, "pages": pages], options: [.prettyPrinted, .sortedKeys])
try json.write(to: output.appendingPathComponent("pdf-layout.json"))
print("Rendered \(document.pageCount) report pages; no application tests run")
