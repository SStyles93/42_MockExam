#include <stdio.h>

int	ft_strcmp(char *s1, char *s2);

/* Only the sign is checked, as strcmp only guarantees the sign. */
int	main(int argc, char **argv)
{
	int	i;
	int	r;

	i = 1;
	while (i + 1 < argc)
	{
		r = ft_strcmp(argv[i], argv[i + 1]);
		printf("%s\n", r < 0 ? "negative" : (r > 0 ? "positive" : "zero"));
		i += 2;
	}
	return (0);
}
