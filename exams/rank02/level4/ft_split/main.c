#include <stdio.h>
#include <stdlib.h>

char	**ft_split(char *str);

int	main(int argc, char **argv)
{
	char	**words;
	int		i;
	int		w;

	i = 1;
	while (i < argc)
	{
		words = ft_split(argv[i]);
		w = 0;
		while (words && words[w])
		{
			printf("[%s] ", words[w]);
			free(words[w++]);
		}
		printf("(%d words)\n", w);
		free(words);
		i++;
	}
	return (0);
}
