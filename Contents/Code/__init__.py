import os
import yaml
from datetime import datetime

class YamlMetadataAgent(Agent.Movies):
    name = 'YamlMetadataAgent'
    languages = [Locale.Language.English]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    def search(self, results, media, lang):
        # 미디어 파일 이름에서 YAML 파일을 찾기 위해 사용
        filename = media.filename
        base_name = os.path.splitext(filename)[0]
        yaml_file = base_name + '.yaml'

        # 파일 이름 기반으로 검색 결과 생성
        results.Append(MetadataSearchResult(
            id=base_name,
            name=os.path.basename(base_name),
            year=None,
            score=100,
            lang=lang
        ))

    def update(self, metadata, media, lang):
        # YAML 파일 경로
        filename = media.items[0].parts[0].file
        base_name = os.path.splitext(filename)[0]
        yaml_file = base_name + '.yaml'

        if os.path.exists(yaml_file):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)

                # 메타데이터 설정
                if 'title' in data:
                    metadata.title = data['title']
                if 'original_title' in data:
                    metadata.original_title = data['original_title']
                if 'title_sort' in data:
                    metadata.title_sort = data['title_sort']
                if 'year' in data:
                    metadata.year = int(data['year'])
                if 'originally_available_at' in data:
                    try:
                        metadata.originally_available_at = datetime.strptime(data['originally_available_at'], '%Y-%m-%d').date()
                    except:
                        pass
                if 'content_rating' in data:
                    metadata.content_rating = data['content_rating']
                if 'tagline' in data:
                    metadata.tagline = data['tagline']
                if 'summary' in data:
                    metadata.summary = data['summary']
                if 'countries' in data:
                    metadata.countries.clear()
                    # countries가 문자열인 경우 리스트로 변환
                    countries = [data['countries']] if isinstance(data['countries'], str) else data['countries']
                    for country in countries:
                        metadata.countries.add(country)
                if 'studio' in data:
                    metadata.studio = data['studio']
                if 'rating' in data:
                    metadata.rating = float(data['rating'])

                # 장르 설정 (genre로 명시된 경우)
                if 'genre' in data:
                    metadata.genres.clear()
                    genres = data['genre'] if isinstance(data['genre'], list) else [data['genre']]
                    for genre in genres:
                        metadata.genres.add(genre)

                # 감독 설정
                if 'directors' in data:
                    metadata.directors.clear()
                    for director in data['directors']:
                        metadata.directors.add(director['name'])

                # 역할 (배우) 설정
                if 'roles' in data:
                    metadata.roles.clear()
                    for role in data['roles']:
                        new_role = metadata.roles.new()
                        new_role.name = role['name']
                        new_role.role = role.get('role', role['name'])
                        if 'photo' in role and role['photo']:
                            try:
                                new_role.photo = role['photo']
                            except:
                                pass

                # 포스터 설정
                if 'posters' in data and data['posters']:
                    metadata.posters.clear()
                    try:
                        metadata.posters['primary'] = HTTP.Request(data['posters']).content
                    except Exception as e:
                        Log('Error loading poster %s: %s' % (data['posters'], str(e)))

                # 아트 설정
                if 'art' in data and data['art']:
                    metadata.art.clear()
                    try:
                        metadata.art['primary'] = HTTP.Request(data['art']).content
                    except Exception as e:
                        Log('Error loading art %s: %s' % (data['art'], str(e)))

            except Exception as e:
                Log('Error reading YAML file %s: %s' % (yaml_file, str(e)))
        else:
            Log('YAML file not found: %s' % yaml_file)
