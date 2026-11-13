import type { XrayScanResult } from "@/types/xrayScan";

interface XrayScanFindingsTableProps {
    result: XrayScanResult;
}

export function XrayScanFindingsTable({ result }: XrayScanFindingsTableProps) {
    const findings = result.findings
        .filter((finding) => finding.label !== "No Finding")
        .sort((left, right) => right.score - left.score);

    return (
        <div className="space-y-2">
            <table className="w-full text-sm">
                <thead>
                    <tr className="border-b text-left text-muted-foreground">
                        <th scope="col" className="py-2 font-medium">
                            Finding
                        </th>
                        <th scope="col" className="py-2 text-right font-medium">
                            Model score
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {findings.map((finding) => (
                        <tr
                            key={finding.label}
                            className="border-b last:border-0"
                        >
                            <th
                                scope="row"
                                className="py-2 text-left font-medium"
                            >
                                {finding.label}
                            </th>
                            <td className="py-2 text-right tabular-nums">
                                {Math.round(finding.score * 100)}%
                            </td>
                        </tr>
                    ))}
                    {findings.length === 0 && (
                        <tr>
                            <td
                                colSpan={2}
                                className="py-2 text-muted-foreground"
                            >
                                No additional findings reported.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
            <p className="text-xs text-muted-foreground">{result.disclaimer}</p>
        </div>
    );
}
