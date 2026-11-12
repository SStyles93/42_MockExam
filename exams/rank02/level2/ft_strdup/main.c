#include <stdio.h>
#include <stdlib.h>

char	*ft_strdup(char *src);

int	main(int argc, char **argv)
{
	char	*dup;
	int		i;

	i = 1;
	while (i < argc)
	{
		dup = ft_strdup(argv[i]);
		if (!dup)
			printf("NULL\n");
		else
		{
			printf("[%s] new pointer: %s\n", dup, dup != argv[i] ? "yes" : "no");
			free(dup);
		}
		i++;
	}
	return (0);
}
