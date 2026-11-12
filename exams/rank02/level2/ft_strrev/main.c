#include <stdio.h>

char	*ft_strrev(char *str);

int	main(int argc, char **argv)
{
	char	*ret;
	int		i;

	i = 1;
	while (i < argc)
	{
		ret = ft_strrev(argv[i]);
		printf("[%s] returns str: %s\n", argv[i], ret == argv[i] ? "yes" : "no");
		i++;
	}
	return (0);
}
