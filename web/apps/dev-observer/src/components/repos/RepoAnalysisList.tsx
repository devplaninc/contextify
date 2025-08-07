import type {GitRepository} from "@devplan/contextify-api";
import {AnalysisList} from "@/components/analysis/AnalysisList.tsx";

export function RepoAnalysisList({repo}: { repo: GitRepository }) {
  return <AnalysisList kind="repos" keysFiler={k => k.key.startsWith(repo.fullName)}/>
}