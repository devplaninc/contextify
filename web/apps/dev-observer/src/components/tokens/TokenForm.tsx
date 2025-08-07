import React, {useState} from "react";
import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {GitProvider, RepoToken} from "@devplan/contextify-api";

import {Button} from "@/components/ui/button.tsx";
import {Input} from "@/components/ui/input.tsx";
import {Checkbox} from "@/components/ui/checkbox.tsx";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage,} from "@/components/ui/form.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";

import {z} from "zod";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {Loader} from "@/components/Loader.tsx";

const tokenFormSchema = z.object({
  namespace: z.string().optional(),
  provider: z.nativeEnum(GitProvider, {
    errorMap: () => ({message: "Please select a valid provider"}),
  }),
  workspace: z.string().optional(),
  repo: z.string().optional(),
  system: z.boolean(),
  token: z.string().min(5, "Token is required").trim(),
});

export type TokenFormData = z.infer<typeof tokenFormSchema>;

interface TokenFormProps {
  onSuccess?: () => void;
}

const TokenForm: React.FC<TokenFormProps> = ({onSuccess}) => {
  const form = useForm<TokenFormData>({
    resolver: zodResolver(tokenFormSchema),
    defaultValues: {provider: GitProvider.BIT_BUCKET, token: "", system: false},
  });
  const {addToken} = useBoundStore()
  const [creating, setCreating] = useState(false);

  const onSubmit = (data: TokenFormData) => {
    setCreating(true);
    void addToken(RepoToken.create({...data})).then(() => {
      form.reset()
      onSuccess?.()
    }).finally(() => setCreating(false));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add New Token</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={(e) => void form.handleSubmit(onSubmit)(e)} className="space-y-4">
            <FormField
              control={form.control}
              name="namespace"
              render={({field}) => (
                <FormItem>
                  <FormLabel>Namespace</FormLabel>
                  <FormControl><Input {...field}/></FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="provider"
              render={({field}) => (
                <FormItem>
                  <FormLabel>Provider</FormLabel>
                  <Select
                    onValueChange={(value) => field.onChange(parseInt(value) as GitProvider)}
                    value={field.value?.toString()}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a provider"/>
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value={GitProvider.GITHUB.toString()}>GitHub</SelectItem>
                      <SelectItem value={GitProvider.BIT_BUCKET.toString()}>BitBucket</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="workspace"
              render={({field}) => (
                <FormItem>
                  <FormLabel>Workspace</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Workspace name (optional)"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="repo"
              render={({field}) => (
                <FormItem>
                  <FormLabel>Repository</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Repository name (optional)"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="system"
              render={({field}) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>System token</FormLabel>
                  </div>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="token"
              render={({field}) => (
                <FormItem>
                  <FormLabel>Token *</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Access token"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage/>
                </FormItem>
              )}
            />

            <Button type="submit" disabled={creating}>
              {creating && <Loader/>} Add Token
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default TokenForm;