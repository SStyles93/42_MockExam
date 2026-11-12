#include <stdio.h>
#include <string.h>

char	*ft_strcpy(char *s1, char *s2);

int	main(int argc, char **argv)
{
	char	buf[4096];
	char	*ret;
	int		i;

	i = 1;
	while (i < argc)
	{
		memset(buf, 'X', sizeof(buf) - 1);
		buf[sizeof(buf) - 1] = '\0';
		ret = ft_strcpy(buf, argv[i]);
		printf("[%s] returns dest: %s\n", buf, ret == buf ? "yes" : "no");
		i++;
	}
	return (0);
}
