\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{notes}[2021/09/01 Trade]

%% Load base
\LoadClass[a4paper]{article}

%% Load additional packages and commands.
% \RequirePackage{custom}

\RequirePackage{geometry}
\RequirePackage{fontspec}
\RequirePackage{tocloft}
\RequirePackage{setspace}
\RequirePackage{graphicx}
\RequirePackage{amsthm} %Math capabilities
\RequirePackage{amssymb} %Math symbols
\RequirePackage{amsmath} %mat capabilities? For having \text{}
\RequirePackage{enumitem} %descriptions with good spacing
\RequirePackage[makeroom]{cancel}
\RequirePackage[dvipsnames]{xcolor} %Colour for todo

%% Additional TeX/LaTeX code...

\author{}
\date{} %To remove date
\setlength{\parindent}{0pt} %To remove indentation

% \renewcommand{\cfttoctitlefont}{\normalfont\Large}% Remove \bfseries from ToC title
\renewcommand{\cftsecfont}{}% Remove \bfseries from section titles in ToC
\renewcommand{\cftsecpagefont}{}% Remove \bfseries from section titles' page in ToC

\newcommand{\TODO}[1]{
\colorbox{BurntOrange}{\textbf{\textsc{TODO}: #1}}
}

\graphicspath{ {./images/} } %Make sure to know if notes/images or respect to tex file

\endinput
