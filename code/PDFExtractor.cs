// Extract text from PDF files

using System.Text;
using iText.Kernel.Pdf;
using iText.Kernel.Pdf.Canvas.Parser;

static class PDFExtractor
{
    // Extract all text from a PDF file
    public static string ExtractText(string pdfPath)
    {
        using var pdfReader = new PdfReader(pdfPath);
        using var pdfDoc = new PdfDocument(pdfReader);

        var text = new StringBuilder();

        // Extract text from each page
        for (int i = 1; i <= pdfDoc.GetNumberOfPages(); i++)
        {
            var page = pdfDoc.GetPage(i);
            var pageText = PdfTextExtractor.GetTextFromPage(page);
            text.AppendLine(pageText);
        }

        return text.ToString();
    }

    // Split text into chunks with overlap
    // $REQ_TREE_001, $REQ_TREE_014, $REQ_TREE_015
    public static List<string> ChunkText(string text, int chunkSize = 1000, int overlap = 100)
    {
        var chunks = new List<string>();
        int pos = 0;

        while (pos < text.Length)
        {
            int end = Math.Min(pos + chunkSize, text.Length);
            chunks.Add(text.Substring(pos, end - pos));

            // Move forward by (chunkSize - overlap) to create overlap
            pos += chunkSize - overlap;

            // Stop if we've reached the end
            if (end >= text.Length)
                break;
        }

        return chunks;
    }
}
