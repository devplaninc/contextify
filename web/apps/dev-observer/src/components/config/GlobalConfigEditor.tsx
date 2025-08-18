import {useFieldArray, useForm} from "react-hook-form";
import {z} from "zod";
import {zodResolver} from "@hookform/resolvers/zod";
import {Analyzer, GlobalConfig} from "@devplan/contextify-api";
import {useCallback} from "react";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {toast} from "sonner";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form.tsx";
import {Input} from "@/components/ui/input.tsx";
import {Button} from "@/components/ui/button.tsx";
import {useGlobalConfig} from "@/hooks/use-config.tsx";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";
import {Separator} from "@/components/ui/separator.tsx";
import {Checkbox} from "@/components/ui/checkbox.tsx";

const analyzerSchema = z.object({
  name: z.string().min(2),
  promptPrefix: z.string().min(2),
  fileName: z.string().min(2),
})

const analysisConfigSchema = z.object({
  repoAnalyzers: z.array(analyzerSchema),
  siteAnalyzers: z.array(analyzerSchema),
  disableMasking: z.boolean(),
  defaultGitChangesAnalyzer: analyzerSchema.optional(),
  defaultAggregatedSummaryAnalyzer: analyzerSchema.optional(),
})

const repoAnalysisConfigFlattenSchema = z.object({
  compress: z.boolean(),
  removeEmptyLines: z.boolean(),
  outStyle: z.string(),
  maxTokensPerChunk: z.coerce.number(),
  maxRepoSizeMb: z.coerce.number(),
  ignorePattern: z.string(),
  largeRepoThresholdMb: z.coerce.number(),
  largeRepoIgnorePattern: z.string(),
  compressLarge: z.boolean(),
  maxFileSizeBytes: z.coerce.number(),
})

const repoAnalysisConfigResearchSchema = z.object({
  maxRepoSizeMb: z.coerce.number(),
  maxIterations: z.coerce.number(),
  generalPrefix: z.string().optional(),
  analyzers: z.array(analyzerSchema),
  reportChunkSize: z.coerce.number(),
  maxToolContentTokens: z.coerce.number(),
})

const repoAnalysisConfigSchema = z.object({
  flatten: repoAnalysisConfigFlattenSchema,
  processingIntervalSec: z.coerce.number(),
  disabled: z.boolean(),
  research: repoAnalysisConfigResearchSchema,
})

const websiteCrawlingConfigSchema = z.object({
  websiteScanTimeoutSeconds: z.coerce.number(),
  scrapyResponseTimeoutSeconds: z.coerce.number(),
  crawlDepth: z.coerce.number(),
  timeoutWithoutDataSeconds: z.coerce.number(),
})

const globalConfigSchema = z.object({
  analysis: analysisConfigSchema,
  repoAnalysis: repoAnalysisConfigSchema,
  websiteCrawling: websiteCrawlingConfigSchema.optional(),
})

export type globalConfigType = z.infer<typeof globalConfigSchema>

export function GlobalConfigEditor() {
  const {config, error} = useGlobalConfig()
  if (!config) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  return <GlobalConfigEditorForm config={config}/>
}

function GlobalConfigEditorForm({config}: { config: GlobalConfig }) {
  const {updateGlobalConfig} = useBoundStore()
  const form = useForm<globalConfigType>({
    resolver: zodResolver(globalConfigSchema),
    defaultValues: config,
  });
  const onSubmit = useCallback((values: globalConfigType) => {
      console.log("Submitting", {values})
      updateGlobalConfig(values)
        .then(() => toast.success("Config updated"))
        .catch(e => {
          toast.error(`Failed to update config: ${e}`)
          throw e
        })
    }
    , [updateGlobalConfig])
  const {fields: repoAnalyzers, remove: removeRepoAnalyzer, append: appendRepoAnalyzer}
    = useFieldArray({name: "analysis.repoAnalyzers", control: form.control});
  const {fields: siteAnalyzers, remove: removeSiteAnalyzer, append: appendSiteAnalyzer}
    = useFieldArray({name: "analysis.siteAnalyzers", control: form.control});
  const {fields: codeResearchAnalyzers, remove: removeCodeResearchAnalyzer, append: appendCodeResearchAnalyzer}
    = useFieldArray({name: "repoAnalysis.research.analyzers", control: form.control});
  return <Form {...form}>
    {/* eslint-disable-next-line @typescript-eslint/no-misused-promises */}
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
      <div className="space-y-4">
        <h2 className="font-semibold text-lg">Repo Analyzers:</h2>
        {repoAnalyzers.map((f, i) => (
          <div key={f.id} className="border rounded-md p-4 space-y-4">
            <FormField
              control={form.control}
              name={`analysis.repoAnalyzers.${i}.name`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`analysis.repoAnalyzers.${i}.promptPrefix`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Prompt Prefix:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer prompt prefix" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`analysis.repoAnalyzers.${i}.fileName`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">File Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer file name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <Button onClick={() => removeRepoAnalyzer(i)}>Remove</Button>
          </div>
        ))}
        <Button onClick={(e) => {
          e.preventDefault()
          appendRepoAnalyzer(Analyzer.create({name: '', promptPrefix: '', fileName: "analysis.md"}))
        }
        }>
          Add Analyzer
        </Button>
      </div>
      <Separator/>
      <div className="space-y-4 border rounded-md p-4">
        <h3 className="font-medium">Research Settings</h3>
        <FormField
          control={form.control}
          name="repoAnalysis.research.generalPrefix"
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[200px]">General prefix:</FormLabel>
              <FormControl><Input {...field} /></FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="repoAnalysis.research.maxRepoSizeMb"
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[200px]">Max Repo Size (MB):</FormLabel>
              <FormControl className="w-[200px]">
                <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="repoAnalysis.research.maxIterations"
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[200px]">Max Iterations:</FormLabel>
              <FormControl className="w-[200px]">
                <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="repoAnalysis.research.reportChunkSize"
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[200px]">Report Chunk Size:</FormLabel>
              <FormControl className="w-[200px]">
                <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="repoAnalysis.research.maxToolContentTokens"
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[200px]">Max tool content in tokens before truncate:</FormLabel>
              <FormControl className="w-[200px]">
                <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <h2 className="font-semibold text-lg">Code Research Analyzers:</h2>
        {codeResearchAnalyzers.map((f, i) => (
          <div key={f.id} className="border rounded-md p-4 space-y-4">
            <FormField
              control={form.control}
              name={`repoAnalysis.research.analyzers.${i}.name`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`repoAnalysis.research.analyzers.${i}.promptPrefix`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Prompt Prefix:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer prompt prefix" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`repoAnalysis.research.analyzers.${i}.fileName`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">File Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer file name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <Button onClick={() => removeCodeResearchAnalyzer(i)}>Remove</Button>
          </div>
        ))}
        <Button onClick={(e) => {
          e.preventDefault()
          appendCodeResearchAnalyzer(Analyzer.create({name: '', promptPrefix: '', fileName: "analysis.md"}))
        }
        }>
          Add Analyzer
        </Button>
      </div>
      <Separator/>
      <div className="border rounded-md p-4 space-y-4">
        <h1>Default git changes analyzer</h1>
        <FormField
          control={form.control}
          name={`analysis.defaultGitChangesAnalyzer.name`}
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[100px]">Name:</FormLabel>
              <FormControl className="w-[200px]">
                <Input placeholder="Analyzer name" {...field}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name={`analysis.defaultGitChangesAnalyzer.promptPrefix`}
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[100px]">Prompt Prefix:</FormLabel>
              <FormControl className="w-[200px]">
                <Input placeholder="Analyzer prompt prefix" {...field}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name={`analysis.defaultGitChangesAnalyzer.fileName`}
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[100px]">File Name:</FormLabel>
              <FormControl className="w-[200px]">
                <Input placeholder="Analyzer file name" {...field}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
      </div>
      <Separator/>
      <div className="border rounded-md p-4 space-y-4">
        <h1>Default aggregated summary analyzer</h1>
        <FormField
          control={form.control}
          name={`analysis.defaultAggregatedSummaryAnalyzer.name`}
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[100px]">Name:</FormLabel>
              <FormControl className="w-[200px]">
                <Input placeholder="Analyzer name" {...field}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name={`analysis.defaultAggregatedSummaryAnalyzer.promptPrefix`}
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[100px]">Prompt Prefix:</FormLabel>
              <FormControl className="w-[200px]">
                <Input placeholder="Analyzer prompt prefix" {...field}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name={`analysis.defaultAggregatedSummaryAnalyzer.fileName`}
          render={({field}) => (
            <FormItem className="flex items-center gap-4">
              <FormLabel className="w-[100px]">File Name:</FormLabel>
              <FormControl className="w-[200px]">
                <Input placeholder="Analyzer file name" {...field}/>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
      </div>
      <Separator/>

      <div className="space-y-4">
        <h2 className="font-semibold text-lg">Site Analyzers:</h2>
        {siteAnalyzers.map((f, i) => (
          <div key={f.id} className="border rounded-md p-4 space-y-4">
            <FormField
              control={form.control}
              name={`analysis.siteAnalyzers.${i}.name`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`analysis.siteAnalyzers.${i}.promptPrefix`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">Prompt Prefix:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer prompt prefix" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name={`analysis.siteAnalyzers.${i}.fileName`}
              render={({field}) => (
                <FormItem className="flex items-center gap-4">
                  <FormLabel className="w-[100px]">File Name:</FormLabel>
                  <FormControl className="w-[200px]">
                    <Input placeholder="Analyzer file name" {...field}/>
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <Button onClick={() => removeSiteAnalyzer(i)}>Remove</Button>
          </div>
        ))}
        <Button onClick={(e) => {
          e.preventDefault()
          appendSiteAnalyzer(Analyzer.create({name: '', promptPrefix: '', fileName: "analysis.md"}))
        }
        }>
          Add Analyzer
        </Button>
      </div>

      <Separator/>
      <FormField
        control={form.control} name="analysis.disableMasking"
        render={({field}) => <FormItem>
          <div className="flex items-center gap-2">
            <FormControl>
              <Checkbox checked={field.value} onCheckedChange={field.onChange}/>
            </FormControl>
            <FormLabel>Disable Traces Masking</FormLabel>
          </div>
          <FormMessage/>
        </FormItem>}
      />
      <Separator/>

      <div className="space-y-4">
        <h2 className="font-semibold text-lg">Repository Analysis Configuration:</h2>

        <div className="border rounded-md p-4 space-y-4">
          <h3 className="font-medium">General Settings</h3>

          <FormField
            control={form.control}
            name="repoAnalysis.processingIntervalSec"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Processing Interval (sec):</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.disabled"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Disabled:</FormLabel>
                <FormControl>
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                  />
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />
        </div>

        <div className="border rounded-md p-4 space-y-4">
          <h3 className="font-medium">Flatten Settings</h3>

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.compress"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Compress:</FormLabel>
                <FormControl>
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                  />
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.removeEmptyLines"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Remove Empty Lines:</FormLabel>
                <FormControl>
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                  />
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.outStyle"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Output Style:</FormLabel>
                <FormControl className="w-[200px]">
                  <Input {...field} />
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.maxTokensPerChunk"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Max Tokens Per Chunk:</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.maxRepoSizeMb"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Max Repo Size (MB):</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.maxFileSizeBytes"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Max File Size (B):</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.ignorePattern"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Ignore Pattern:</FormLabel>
                <FormControl>
                  <Input {...field} value={field.value || ""}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.largeRepoIgnorePattern"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Large Repo Ignore Pattern:</FormLabel>
                <FormControl>
                  <Input {...field} value={field.value || ""}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.largeRepoThresholdMb"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Large Repo Threshold (MB):</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="repoAnalysis.flatten.compressLarge"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Compress Large:</FormLabel>
                <FormControl>
                  <input
                    type="checkbox"
                    checked={field.value}
                    onChange={field.onChange}
                  />
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />
        </div>
      </div>

      <Separator/>

      <div className="space-y-4">
        <h2 className="font-semibold text-lg">Website Crawling Configuration:</h2>

        <div className="border rounded-md p-4 space-y-4">
          <h3 className="font-medium">Crawling Parameters</h3>

          <FormField
            control={form.control}
            name="websiteCrawling.websiteScanTimeoutSeconds"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Website Scan Timeout (seconds):</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="websiteCrawling.scrapyResponseTimeoutSeconds"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Response Timeout (seconds):</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="websiteCrawling.crawlDepth"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Crawl Depth:</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="websiteCrawling.timeoutWithoutDataSeconds"
            render={({field}) => (
              <FormItem className="flex items-center gap-4">
                <FormLabel className="w-[200px]">Timeout Without Data (seconds):</FormLabel>
                <FormControl className="w-[200px]">
                  <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))}/>
                </FormControl>
                <FormMessage/>
              </FormItem>
            )}
          />
        </div>
      </div>

      <Button role="submit">
        Submit
      </Button>
    </form>
  </Form>
}
