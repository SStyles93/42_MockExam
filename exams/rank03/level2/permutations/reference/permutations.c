#include <stdlib.h>
#include <unistd.h>

static void	sort(char *s, int n)
{
	int		i;
	int		j;
	char	tmp;

	i = 1;
	while (i < n)
	{
		j = i;
		while (j > 0 && s[j - 1] > s[j])
		{
			tmp = s[j];
			s[j] = s[j - 1];
			s[j - 1] = tmp;
			j--;
		}
		i++;
	}
}

static void	permute(char *sorted, char *out, int *used, int depth, int n)
{
	int	i;

	if (depth == n)
	{
		write(1, out, n);
		write(1, "\n", 1);
		return ;
	}
	i = 0;
	while (i < n)
	{
		if (!used[i])
		{
			used[i] = 1;
			out[depth] = sorted[i];
			permute(sorted, out, used, depth + 1, n);
			used[i] = 0;
		}
		i++;
	}
}

int	main(int argc, char **argv)
{
	char	*sorted;
	char	*out;
	int		*used;
	int		n;

	if (argc != 2)
		return (1);
	n = 0;
	while (argv[1][n])
		n++;
	sorted = malloc(n + 1);
	out = malloc(n + 1);
	used = calloc(n + 1, sizeof(int));
	if (!sorted || !out || !used)
		return (1);
	n = -1;
	while (argv[1][++n])
		sorted[n] = argv[1][n];
	sort(sorted, n);
	permute(sorted, out, used, 0, n);
	free(sorted);
	free(out);
	free(used);
	return (0);
}
