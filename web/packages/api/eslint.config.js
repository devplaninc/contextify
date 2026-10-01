import tseslint from 'typescript-eslint';

export default tseslint.config(
    {ignores: ['dist/**', 'src/pb/**']},
    ...tseslint.configs.recommended,
);
